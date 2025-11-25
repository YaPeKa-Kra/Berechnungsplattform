(* ============================================================================
   Global Variable List: GVL_Joystick
   Development Environment: CODESYS
   PLC Hardware: Intercontrol DIGSY Fusion S
   Description: Global variables for joystick and CAN communication system
   ============================================================================ *)
{attribute 'qualified_only'}
VAR_GLOBAL
    (* CAN Configuration *)
    CAN_BAUDRATE        : DWORD := 250000;      (* CAN Baudrate in bit/s *)
    JOYSTICK_BASE_ID    : DWORD := 16#180;      (* Base CAN ID for Gessmann joystick *)
    THRUST_LEVER_ID     : DWORD := 16#181;      (* CAN ID for thrust lever *)
    BUTTONS_ID          : DWORD := 16#182;      (* CAN ID for buttons *)
    COMM_TIMEOUT        : TIME := T#500MS;      (* Communication timeout *)
    CYCLE_TIME          : TIME := T#10MS;       (* PLC cycle time *)
    
    (* Deadzone settings in percent *)
    DEADZONE_X          : REAL := 5.0;          (* Deadzone for X-axis *)
    DEADZONE_Y          : REAL := 5.0;          (* Deadzone for Y-axis *)
    DEADZONE_Z          : REAL := 5.0;          (* Deadzone for Z-axis/rotation *)
    DEADZONE_THRUST     : REAL := 2.0;          (* Deadzone for thrust lever *)
    
    (* Thrust limits and rates *)
    MAX_THRUST          : REAL := 100.0;        (* Maximum thrust limit (%) *)
    MIN_THRUST          : REAL := -30.0;        (* Minimum thrust limit (%) *)
    RAMP_UP_RATE        : REAL := 50.0;         (* Acceleration rate (%/s) *)
    RAMP_DOWN_RATE      : REAL := 75.0;         (* Deceleration rate (%/s) *)
    EMERGENCY_RAMP_RATE : REAL := 200.0;        (* Emergency stop rate (%/s) *)
    DEADBAND            : REAL := 2.0;          (* Input deadband (%) *)
    
    (* System status flags - read/write from other programs *)
    System_Ready        : BOOL := FALSE;        (* System is ready for operation *)
    Emergency_Active    : BOOL := FALSE;        (* Emergency stop is active *)
    CAN_Online          : BOOL := FALSE;        (* CAN communication is online *)
    Joystick_Online     : BOOL := FALSE;        (* Joystick is communicating *)
    
    (* Error codes *)
    System_Error_Code   : DWORD := 0;           (* Current system error code *)
    (* Error code definitions:
       0 = No error
       1 = CAN not initialized
       2 = Joystick offline/timeout
       3 = Joystick communication error
       4 = Emergency stop active
    *)
END_VAR
