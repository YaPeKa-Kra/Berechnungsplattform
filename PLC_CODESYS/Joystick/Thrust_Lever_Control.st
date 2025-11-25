(* ============================================================================
   Thrust Lever Control Function Block
   Development Environment: CODESYS
   PLC Hardware: Intercontrol DIGSY Fusion S
   Description: Advanced thrust lever control with ramping, limits, and modes
   ============================================================================ *)

TYPE Thrust_Mode :
(
    THRUST_MODE_MANUAL := 0,        (* Direct joystick control *)
    THRUST_MODE_CRUISE := 1,        (* Cruise control / hold speed *)
    THRUST_MODE_RAMP := 2,          (* Ramped acceleration/deceleration *)
    THRUST_MODE_EMERGENCY := 3      (* Emergency stop *)
);
END_TYPE

TYPE Thrust_Status :
STRUCT
    eMode           : Thrust_Mode;      (* Current operating mode *)
    rCurrentThrust  : REAL;             (* Current thrust output (%) *)
    rTargetThrust   : REAL;             (* Target thrust (%) *)
    rRampRate       : REAL;             (* Current ramp rate (%/s) *)
    bLimitActive    : BOOL;             (* Limit is active *)
    bRamping        : BOOL;             (* Currently ramping *)
    bEmergency      : BOOL;             (* Emergency mode active *)
END_STRUCT
END_TYPE

(* ============================================================================
   FUNCTION_BLOCK: FB_Thrust_Lever_Control
   Description: Advanced thrust lever control with multiple operating modes
   ============================================================================ *)
FUNCTION_BLOCK FB_Thrust_Lever_Control
VAR_INPUT
    bEnable             : BOOL := FALSE;        (* Enable control *)
    rThrustLeverInput   : REAL := 0.0;          (* Raw thrust lever input (-100 to +100 %) *)
    eRequestedMode      : Thrust_Mode := THRUST_MODE_MANUAL;  (* Requested mode *)
    bEmergencyStop      : BOOL := FALSE;        (* Emergency stop trigger *)
    bCruiseSet          : BOOL := FALSE;        (* Set cruise control *)
    bCruiseResume       : BOOL := FALSE;        (* Resume cruise control *)
    bCruiseCancel       : BOOL := FALSE;        (* Cancel cruise control *)
    
    (* Configuration parameters *)
    rMaxThrust          : REAL := 100.0;        (* Maximum thrust limit (%) *)
    rMinThrust          : REAL := -100.0;       (* Minimum thrust limit (%) *)
    rRampUpRate         : REAL := 50.0;         (* Acceleration rate (%/s) *)
    rRampDownRate       : REAL := 75.0;         (* Deceleration rate (%/s) *)
    rEmergencyRampRate  : REAL := 200.0;        (* Emergency deceleration rate (%/s) *)
    rDeadband           : REAL := 2.0;          (* Input deadband (%) *)
    tCycleTime          : TIME := T#10MS;       (* PLC cycle time for rate calculations *)
END_VAR

VAR_OUTPUT
    rThrustOutput       : REAL := 0.0;          (* Final thrust output (-100 to +100 %) *)
    stStatus            : Thrust_Status;        (* Current status *)
    bActive             : BOOL := FALSE;        (* Control is active *)
    bAtTarget           : BOOL := FALSE;        (* Output equals target *)
END_VAR

VAR
    rInternalTarget     : REAL := 0.0;          (* Internal target thrust *)
    rInternalOutput     : REAL := 0.0;          (* Internal output value *)
    rCruiseSetpoint     : REAL := 0.0;          (* Stored cruise setpoint *)
    bCruiseActive       : BOOL := FALSE;        (* Cruise control is active *)
    rCycleTimeSeconds   : REAL := 0.01;         (* Cycle time in seconds *)
    rDelta              : REAL := 0.0;          (* Change per cycle *)
    bPrevCruiseSet      : BOOL := FALSE;        (* Previous cruise set state *)
END_VAR

(* Calculate cycle time in seconds *)
rCycleTimeSeconds := TIME_TO_REAL(tCycleTime) / 1000.0;

(* Main execution *)
IF NOT bEnable THEN
    rInternalOutput := 0.0;
    rInternalTarget := 0.0;
    rThrustOutput := 0.0;
    bActive := FALSE;
    stStatus.eMode := THRUST_MODE_MANUAL;
    stStatus.bEmergency := FALSE;
    bCruiseActive := FALSE;
    RETURN;
END_IF

bActive := TRUE;

(* Emergency stop handling - highest priority *)
IF bEmergencyStop THEN
    stStatus.eMode := THRUST_MODE_EMERGENCY;
    stStatus.bEmergency := TRUE;
    rInternalTarget := 0.0;
    bCruiseActive := FALSE;
    
    (* Fast ramp to zero *)
    IF rInternalOutput > 0.0 THEN
        rInternalOutput := rInternalOutput - (rEmergencyRampRate * rCycleTimeSeconds);
        IF rInternalOutput < 0.0 THEN
            rInternalOutput := 0.0;
        END_IF
    ELSIF rInternalOutput < 0.0 THEN
        rInternalOutput := rInternalOutput + (rEmergencyRampRate * rCycleTimeSeconds);
        IF rInternalOutput > 0.0 THEN
            rInternalOutput := 0.0;
        END_IF
    END_IF
    
ELSE
    stStatus.bEmergency := FALSE;
    
    (* Mode handling *)
    CASE eRequestedMode OF
        THRUST_MODE_MANUAL:
            stStatus.eMode := THRUST_MODE_MANUAL;
            bCruiseActive := FALSE;
            
            (* Apply deadband *)
            IF ABS(rThrustLeverInput) < rDeadband THEN
                rInternalTarget := 0.0;
            ELSE
                rInternalTarget := rThrustLeverInput;
            END_IF
            
            (* Apply limits *)
            IF rInternalTarget > rMaxThrust THEN
                rInternalTarget := rMaxThrust;
                stStatus.bLimitActive := TRUE;
            ELSIF rInternalTarget < rMinThrust THEN
                rInternalTarget := rMinThrust;
                stStatus.bLimitActive := TRUE;
            ELSE
                stStatus.bLimitActive := FALSE;
            END_IF
            
            (* Direct output in manual mode *)
            rInternalOutput := rInternalTarget;
            
        THRUST_MODE_CRUISE:
            stStatus.eMode := THRUST_MODE_CRUISE;
            
            (* Cruise set button rising edge *)
            IF bCruiseSet AND NOT bPrevCruiseSet THEN
                rCruiseSetpoint := rInternalOutput;
                bCruiseActive := TRUE;
            END_IF
            bPrevCruiseSet := bCruiseSet;
            
            (* Resume cruise *)
            IF bCruiseResume AND rCruiseSetpoint <> 0.0 THEN
                bCruiseActive := TRUE;
            END_IF
            
            (* Cancel cruise *)
            IF bCruiseCancel THEN
                bCruiseActive := FALSE;
            END_IF
            
            (* Cruise operation *)
            IF bCruiseActive THEN
                rInternalTarget := rCruiseSetpoint;
            ELSE
                (* Fall back to manual input if cruise not active *)
                IF ABS(rThrustLeverInput) < rDeadband THEN
                    rInternalTarget := 0.0;
                ELSE
                    rInternalTarget := rThrustLeverInput;
                END_IF
            END_IF
            
            (* Ramp to target *)
            RampToTarget();
            
        THRUST_MODE_RAMP:
            stStatus.eMode := THRUST_MODE_RAMP;
            bCruiseActive := FALSE;
            
            (* Apply deadband *)
            IF ABS(rThrustLeverInput) < rDeadband THEN
                rInternalTarget := 0.0;
            ELSE
                rInternalTarget := rThrustLeverInput;
            END_IF
            
            (* Apply limits *)
            IF rInternalTarget > rMaxThrust THEN
                rInternalTarget := rMaxThrust;
                stStatus.bLimitActive := TRUE;
            ELSIF rInternalTarget < rMinThrust THEN
                rInternalTarget := rMinThrust;
                stStatus.bLimitActive := TRUE;
            ELSE
                stStatus.bLimitActive := FALSE;
            END_IF
            
            (* Ramp to target *)
            RampToTarget();
            
        ELSE
            (* Unknown mode - default to manual *)
            stStatus.eMode := THRUST_MODE_MANUAL;
            rInternalOutput := rThrustLeverInput;
    END_CASE
END_IF

(* Update status *)
stStatus.rCurrentThrust := rInternalOutput;
stStatus.rTargetThrust := rInternalTarget;
bAtTarget := ABS(rInternalOutput - rInternalTarget) < 0.1;

(* Set output *)
rThrustOutput := rInternalOutput;

END_FUNCTION_BLOCK

(* ============================================================================
   ACTION: RampToTarget
   Description: Ramps output towards target with configurable rates
   ============================================================================ *)
ACTION RampToTarget

(* Calculate required change *)
rDelta := rInternalTarget - rInternalOutput;

IF ABS(rDelta) < 0.1 THEN
    (* Close enough - snap to target *)
    rInternalOutput := rInternalTarget;
    stStatus.bRamping := FALSE;
    stStatus.rRampRate := 0.0;
ELSE
    stStatus.bRamping := TRUE;
    
    IF rDelta > 0.0 THEN
        (* Ramping up (accelerating) *)
        stStatus.rRampRate := rRampUpRate;
        rInternalOutput := rInternalOutput + (rRampUpRate * rCycleTimeSeconds);
        IF rInternalOutput > rInternalTarget THEN
            rInternalOutput := rInternalTarget;
        END_IF
    ELSE
        (* Ramping down (decelerating) *)
        stStatus.rRampRate := rRampDownRate;
        rInternalOutput := rInternalOutput - (rRampDownRate * rCycleTimeSeconds);
        IF rInternalOutput < rInternalTarget THEN
            rInternalOutput := rInternalTarget;
        END_IF
    END_IF
END_IF

END_ACTION
