(* ============================================================================
   Main Control Program
   Development Environment: CODESYS
   PLC Hardware: Intercontrol DIGSY Fusion S
   Description: Main control program integrating CAN communication,
                Gessmann joystick, and thrust lever control
   ============================================================================ *)

PROGRAM PLC_PRG
VAR
    (* CAN Interface *)
    fbCANInterface      : FB_CAN_Interface;
    bCANEnable          : BOOL := TRUE;
    dwCANBaudrate       : DWORD := 250000;      (* 250 kbit/s standard for Gessmann *)
    
    (* Joystick Handler *)
    fbJoystick          : FB_Gessmann_Joystick;
    bJoystickEnable     : BOOL := TRUE;
    dwJoystickBaseID    : DWORD := 16#180;      (* Base CAN ID for Gessmann joystick *)
    
    (* Thrust Lever Control *)
    fbThrustControl     : FB_Thrust_Lever_Control;
    bThrustEnable       : BOOL := TRUE;
    eThrustMode         : Thrust_Mode := THRUST_MODE_RAMP;
    
    (* Control outputs *)
    rDriveSpeedX        : REAL := 0.0;          (* X-axis drive speed command *)
    rDriveSpeedY        : REAL := 0.0;          (* Y-axis drive speed command *)
    rRotationSpeed      : REAL := 0.0;          (* Rotation speed command *)
    rThrustCommand      : REAL := 0.0;          (* Thrust command *)
    
    (* Status and diagnostics *)
    bSystemReady        : BOOL := FALSE;
    bCANOnline          : BOOL := FALSE;
    bJoystickOnline     : BOOL := FALSE;
    bThrustActive       : BOOL := FALSE;
    dwErrorCode         : DWORD := 0;
    
    (* Safety *)
    bEmergencyStop      : BOOL := FALSE;
    bSafetyOK           : BOOL := TRUE;
    
    (* Timing *)
    tCycleTime          : TIME := T#10MS;
END_VAR

(* ============================================================================
   Main Control Logic
   ============================================================================ *)

(* Initialize CAN Interface *)
fbCANInterface(
    bEnable := bCANEnable,
    dwBaudrate := dwCANBaudrate
);

bCANOnline := fbCANInterface.bInitialized;

(* Process Joystick *)
fbJoystick(
    bEnable := bJoystickEnable AND bCANOnline,
    stCANMessage := fbCANInterface.stRxMessage,
    bNewCANMessage := fbCANInterface.bMessageReceived,
    dwJoystickCANID := dwJoystickBaseID,
    dwThrustLeverCANID := dwJoystickBaseID + 1,
    dwButtonsCANID := dwJoystickBaseID + 2,
    tTimeout := T#500MS,
    rDeadzoneX := 5.0,
    rDeadzoneY := 5.0,
    rDeadzoneZ := 5.0,
    rDeadzoneThrustLever := 2.0
);

bJoystickOnline := fbJoystick.bOnline;

(* Process Thrust Lever Control *)
fbThrustControl(
    bEnable := bThrustEnable AND bJoystickOnline AND bSafetyOK,
    rThrustLeverInput := fbJoystick.rThrustLever,
    eRequestedMode := eThrustMode,
    bEmergencyStop := bEmergencyStop,
    bCruiseSet := fbJoystick.stJoystickData.bButton1,
    bCruiseResume := fbJoystick.stJoystickData.bButton2,
    bCruiseCancel := fbJoystick.stJoystickData.bButton3,
    rMaxThrust := 100.0,
    rMinThrust := -30.0,    (* Limit reverse thrust *)
    rRampUpRate := 50.0,
    rRampDownRate := 75.0,
    rEmergencyRampRate := 200.0,
    rDeadband := 2.0,
    tCycleTime := tCycleTime
);

bThrustActive := fbThrustControl.bActive;

(* Map joystick outputs to control commands *)
IF bSafetyOK AND NOT bEmergencyStop THEN
    (* Normal operation *)
    rDriveSpeedX := fbJoystick.rAxisX;
    rDriveSpeedY := fbJoystick.rAxisY;
    rRotationSpeed := fbJoystick.rAxisZ;
    rThrustCommand := fbThrustControl.rThrustOutput;
ELSE
    (* Safe state - all outputs to zero *)
    rDriveSpeedX := 0.0;
    rDriveSpeedY := 0.0;
    rRotationSpeed := 0.0;
    rThrustCommand := 0.0;
END_IF

(* System ready status *)
bSystemReady := bCANOnline AND bJoystickOnline AND bSafetyOK AND NOT bEmergencyStop;

(* Error handling *)
IF NOT bCANOnline THEN
    dwErrorCode := 1;   (* CAN not initialized *)
ELSIF NOT bJoystickOnline THEN
    dwErrorCode := 2;   (* Joystick offline *)
ELSIF fbJoystick.bError THEN
    dwErrorCode := 3;   (* Joystick error *)
ELSIF fbThrustControl.stStatus.bEmergency THEN
    dwErrorCode := 4;   (* Emergency stop active *)
ELSE
    dwErrorCode := 0;   (* No error *)
END_IF

END_PROGRAM

(* ============================================================================
   GLOBAL VARIABLE LIST: GVL_Joystick
   Description: Global variables for joystick system
   ============================================================================ *)
{attribute 'qualified_only'}
VAR_GLOBAL
    (* Configuration *)
    CAN_BAUDRATE        : DWORD := 250000;
    JOYSTICK_BASE_ID    : DWORD := 16#180;
    COMM_TIMEOUT        : TIME := T#500MS;
    CYCLE_TIME          : TIME := T#10MS;
    
    (* Deadzone settings *)
    DEADZONE_X          : REAL := 5.0;
    DEADZONE_Y          : REAL := 5.0;
    DEADZONE_Z          : REAL := 5.0;
    DEADZONE_THRUST     : REAL := 2.0;
    
    (* Thrust limits *)
    MAX_THRUST          : REAL := 100.0;
    MIN_THRUST          : REAL := -30.0;
    RAMP_UP_RATE        : REAL := 50.0;
    RAMP_DOWN_RATE      : REAL := 75.0;
    
    (* Status flags *)
    System_Ready        : BOOL := FALSE;
    Emergency_Active    : BOOL := FALSE;
END_VAR
