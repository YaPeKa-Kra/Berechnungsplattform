(* ============================================================================
   Gessmann Joystick / Thrust Lever CAN Interface
   Development Environment: CODESYS
   PLC Hardware: Intercontrol DIGSY Fusion S
   Description: Function block for reading Gessmann joystick and thrust lever
                signals via CAN bus
   ============================================================================ *)

TYPE Joystick_Axis :
STRUCT
    nRawValue       : INT;          (* Raw value from CAN message *)
    rScaledValue    : REAL;         (* Scaled value (-100.0 to +100.0 %) *)
    rDeadzone       : REAL := 5.0;  (* Deadzone in percent *)
    bInDeadzone     : BOOL;         (* Axis is in deadzone *)
    nMin            : INT := -32768;(* Minimum raw value *)
    nMax            : INT := 32767; (* Maximum raw value *)
    nCenter         : INT := 0;     (* Center/neutral raw value *)
END_STRUCT
END_TYPE

TYPE Gessmann_Joystick_Data :
STRUCT
    (* Axis data *)
    stAxisX         : Joystick_Axis;    (* X-Axis (left/right) *)
    stAxisY         : Joystick_Axis;    (* Y-Axis (forward/backward) *)
    stAxisZ         : Joystick_Axis;    (* Z-Axis / Twist (rotation) *)
    stThrustLever   : Joystick_Axis;    (* Thrust lever position *)
    
    (* Button states *)
    bButton1        : BOOL := FALSE;    (* Button 1 state *)
    bButton2        : BOOL := FALSE;    (* Button 2 state *)
    bButton3        : BOOL := FALSE;    (* Button 3 state *)
    bButton4        : BOOL := FALSE;    (* Button 4 state *)
    bButton5        : BOOL := FALSE;    (* Button 5 state *)
    bButton6        : BOOL := FALSE;    (* Button 6 state *)
    bButton7        : BOOL := FALSE;    (* Button 7 state *)
    bButton8        : BOOL := FALSE;    (* Button 8 state *)
    
    (* Status *)
    bOnline         : BOOL := FALSE;    (* Joystick communication active *)
    bError          : BOOL := FALSE;    (* Error flag *)
    dwErrorCode     : DWORD := 0;       (* Error code *)
END_STRUCT
END_TYPE

(* ============================================================================
   FUNCTION_BLOCK: FB_Gessmann_Joystick
   Description: Gessmann joystick/thrust lever handler via CAN
   ============================================================================ *)
FUNCTION_BLOCK FB_Gessmann_Joystick
VAR_INPUT
    bEnable             : BOOL := FALSE;        (* Enable joystick processing *)
    stCANMessage        : CAN_Message;          (* Incoming CAN message *)
    bNewCANMessage      : BOOL := FALSE;        (* New CAN message received *)
    dwJoystickCANID     : DWORD := 16#180;      (* Base CAN ID for joystick *)
    dwThrustLeverCANID  : DWORD := 16#181;      (* CAN ID for thrust lever *)
    dwButtonsCANID      : DWORD := 16#182;      (* CAN ID for buttons *)
    tTimeout            : TIME := T#500MS;      (* Communication timeout *)
    rDeadzoneX          : REAL := 5.0;          (* Deadzone for X-axis in % *)
    rDeadzoneY          : REAL := 5.0;          (* Deadzone for Y-axis in % *)
    rDeadzoneZ          : REAL := 5.0;          (* Deadzone for Z-axis in % *)
    rDeadzoneThrustLever: REAL := 2.0;          (* Deadzone for thrust lever in % *)
END_VAR

VAR_OUTPUT
    stJoystickData      : Gessmann_Joystick_Data;   (* Complete joystick data *)
    rAxisX              : REAL := 0.0;              (* X-Axis scaled output *)
    rAxisY              : REAL := 0.0;              (* Y-Axis scaled output *)
    rAxisZ              : REAL := 0.0;              (* Z-Axis scaled output *)
    rThrustLever        : REAL := 0.0;              (* Thrust lever scaled output *)
    bOnline             : BOOL := FALSE;            (* Communication status *)
    bError              : BOOL := FALSE;            (* Error flag *)
END_VAR

VAR
    tCommTimeout        : TON;                      (* Communication timeout timer *)
    bMessageReceived    : BOOL := FALSE;            (* Flag for received message *)
    dwLastMessageTime   : DWORD := 0;               (* Timestamp of last message *)
END_VAR

(* Main execution *)
IF NOT bEnable THEN
    (* Reset all outputs when disabled *)
    stJoystickData.bOnline := FALSE;
    bOnline := FALSE;
    rAxisX := 0.0;
    rAxisY := 0.0;
    rAxisZ := 0.0;
    rThrustLever := 0.0;
    RETURN;
END_IF

(* Set deadzone values *)
stJoystickData.stAxisX.rDeadzone := rDeadzoneX;
stJoystickData.stAxisY.rDeadzone := rDeadzoneY;
stJoystickData.stAxisZ.rDeadzone := rDeadzoneZ;
stJoystickData.stThrustLever.rDeadzone := rDeadzoneThrustLever;

(* Process incoming CAN messages *)
IF bNewCANMessage THEN
    bMessageReceived := TRUE;
    
    (* Process Joystick axes message *)
    IF stCANMessage.ID = dwJoystickCANID THEN
        (* Parse X-Axis from bytes 0-1 (high byte first) *)
        stJoystickData.stAxisX.nRawValue := SHL(BYTE_TO_INT(stCANMessage.Data[0]), 8) 
                                          + BYTE_TO_INT(stCANMessage.Data[1]);
        
        (* Parse Y-Axis from bytes 2-3 *)
        stJoystickData.stAxisY.nRawValue := SHL(BYTE_TO_INT(stCANMessage.Data[2]), 8) 
                                          + BYTE_TO_INT(stCANMessage.Data[3]);
        
        (* Parse Z-Axis from bytes 4-5 *)
        stJoystickData.stAxisZ.nRawValue := SHL(BYTE_TO_INT(stCANMessage.Data[4]), 8) 
                                          + BYTE_TO_INT(stCANMessage.Data[5]);
        
        (* Scale and apply deadzone to each axis *)
        ScaleAxis(stAxis := stJoystickData.stAxisX);
        ScaleAxis(stAxis := stJoystickData.stAxisY);
        ScaleAxis(stAxis := stJoystickData.stAxisZ);
        
        (* Update outputs *)
        rAxisX := stJoystickData.stAxisX.rScaledValue;
        rAxisY := stJoystickData.stAxisY.rScaledValue;
        rAxisZ := stJoystickData.stAxisZ.rScaledValue;
        
    (* Process Thrust Lever message *)
    ELSIF stCANMessage.ID = dwThrustLeverCANID THEN
        (* Parse Thrust Lever from bytes 0-1 *)
        stJoystickData.stThrustLever.nRawValue := SHL(BYTE_TO_INT(stCANMessage.Data[0]), 8) 
                                                + BYTE_TO_INT(stCANMessage.Data[1]);
        
        (* Scale and apply deadzone *)
        ScaleAxis(stAxis := stJoystickData.stThrustLever);
        rThrustLever := stJoystickData.stThrustLever.rScaledValue;
        
    (* Process Buttons message *)
    ELSIF stCANMessage.ID = dwButtonsCANID THEN
        (* Parse button states from byte 0 *)
        stJoystickData.bButton1 := (stCANMessage.Data[0] AND 16#01) <> 0;
        stJoystickData.bButton2 := (stCANMessage.Data[0] AND 16#02) <> 0;
        stJoystickData.bButton3 := (stCANMessage.Data[0] AND 16#04) <> 0;
        stJoystickData.bButton4 := (stCANMessage.Data[0] AND 16#08) <> 0;
        stJoystickData.bButton5 := (stCANMessage.Data[0] AND 16#10) <> 0;
        stJoystickData.bButton6 := (stCANMessage.Data[0] AND 16#20) <> 0;
        stJoystickData.bButton7 := (stCANMessage.Data[0] AND 16#40) <> 0;
        stJoystickData.bButton8 := (stCANMessage.Data[0] AND 16#80) <> 0;
    END_IF
    
    (* Reset timeout timer on any valid message *)
    tCommTimeout(IN := FALSE);
END_IF

(* Communication timeout handling *)
tCommTimeout(IN := bEnable, PT := tTimeout);
IF tCommTimeout.Q THEN
    (* Timeout occurred - no message received within timeout period *)
    stJoystickData.bOnline := FALSE;
    stJoystickData.bError := TRUE;
    stJoystickData.dwErrorCode := 1; (* Timeout error *)
    bOnline := FALSE;
    bError := TRUE;
    
    (* Reset outputs to safe values *)
    rAxisX := 0.0;
    rAxisY := 0.0;
    rAxisZ := 0.0;
    rThrustLever := 0.0;
ELSE
    IF bMessageReceived THEN
        stJoystickData.bOnline := TRUE;
        stJoystickData.bError := FALSE;
        stJoystickData.dwErrorCode := 0;
        bOnline := TRUE;
        bError := FALSE;
    END_IF
END_IF

END_FUNCTION_BLOCK

(* ============================================================================
   ACTION: ScaleAxis
   Description: Scales raw joystick axis value to percentage and applies deadzone
   ============================================================================ *)
ACTION ScaleAxis
VAR_IN_OUT
    stAxis  : Joystick_Axis;
END_VAR

VAR
    rRawPercent : REAL;
    rRange      : REAL;
END_VAR

(* Calculate percentage from raw value *)
IF stAxis.nRawValue >= stAxis.nCenter THEN
    (* Positive direction *)
    rRange := INT_TO_REAL(stAxis.nMax - stAxis.nCenter);
    IF rRange > 0.0 THEN
        rRawPercent := INT_TO_REAL(stAxis.nRawValue - stAxis.nCenter) / rRange * 100.0;
    ELSE
        rRawPercent := 0.0;
    END_IF
ELSE
    (* Negative direction *)
    rRange := INT_TO_REAL(stAxis.nCenter - stAxis.nMin);
    IF rRange > 0.0 THEN
        rRawPercent := INT_TO_REAL(stAxis.nRawValue - stAxis.nCenter) / rRange * 100.0;
    ELSE
        rRawPercent := 0.0;
    END_IF
END_IF

(* Limit to valid range *)
IF rRawPercent > 100.0 THEN
    rRawPercent := 100.0;
ELSIF rRawPercent < -100.0 THEN
    rRawPercent := -100.0;
END_IF

(* Apply deadzone *)
IF ABS(rRawPercent) < stAxis.rDeadzone THEN
    stAxis.rScaledValue := 0.0;
    stAxis.bInDeadzone := TRUE;
ELSE
    (* Scale remaining range to full output range *)
    IF rRawPercent > 0.0 THEN
        stAxis.rScaledValue := (rRawPercent - stAxis.rDeadzone) / (100.0 - stAxis.rDeadzone) * 100.0;
    ELSE
        stAxis.rScaledValue := (rRawPercent + stAxis.rDeadzone) / (100.0 - stAxis.rDeadzone) * 100.0;
    END_IF
    stAxis.bInDeadzone := FALSE;
END_IF

END_ACTION
