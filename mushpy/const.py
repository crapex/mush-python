# -*- coding:utf-8 -*-

# mushclient中常用的常量定义

class Returns:
    '''
    各类返回值常量定义
    '''
    eOK = 0 # No error
    eWorldOpen = 30001 # The world is already open
    eWorldClosed = 30002 # The world is closed, this action cannot be performed
    eNoNameSpecified = 30003 # No name has been specified where one is required
    eCannotPlaySound = 30004 # The sound file could not be played
    eTriggerNotFound = 30005 # The specified trigger name does not exist
    eTriggerAlreadyExists = 30006 # Attempt to add a trigger that already exists
    eTriggerCannotBeEmpty = 30007 # The trigger "match" string cannot be empty
    eInvalidObjectLabel = 30008 # The name of this object is invalid
    eScriptNameNotLocated = 30009 # Script name is not in the script file
    eAliasNotFound = 30010 # The specified alias name does not exist
    eAliasAlreadyExists = 30011 # Attempt to add a alias that already exists
    eAliasCannotBeEmpty = 30012 # The alias "match" string cannot be empty
    eCouldNotOpenFile = 30013 # Unable to open requested file
    eLogFileNotOpen = 30014 # Log file was not open
    eLogFileAlreadyOpen = 30015 # Log file was already open
    eLogFileBadWrite = 30016 # Bad write to log file
    eTimerNotFound = 30017 # The specified timer name does not exist
    eTimerAlreadyExists = 30018 # Attempt to add a timer that already exists
    eVariableNotFound = 30019 # Attempt to delete a variable that does not exist
    eCommandNotEmpty = 30020 # Attempt to use SetCommand with a non-empty command window
    eBadRegularExpression = 30021 # Bad regular expression syntax
    eTimeInvalid = 30022 # Time given to AddTimer is invalid
    eBadMapItem = 30023 # Direction given to AddToMapper is invalid
    eNoMapItems = 30024 # No items in mapper
    eUnknownOption = 30025 # Option name not found
    eOptionOutOfRange = 30026 # New value for option is out of range
    eTriggerSequenceOutOfRange = 30027 # Trigger sequence value invalid
    eTriggerSendToInvalid = 30028 # Where to send trigger text to is invalid
    eTriggerLabelNotSpecified = 30029 # Trigger label not specified/invalid for 'send to variable'
    ePluginFileNotFound = 30030 # File name specified for plugin not found
    eProblemsLoadingPlugin = 30031 # There was a parsing or other problem loading the plugin
    ePluginCannotSetOption = 30032 # Plugin is not allowed to set this option
    ePluginCannotGetOption = 30033 # Plugin is not allowed to get this option
    eNoSuchPlugin = 30034 # Requested plugin is not installed
    eNotAPlugin = 30035 # Only a plugin can do this
    eNoSuchRoutine = 30036 # Plugin does not support that subroutine (subroutine not in script)
    ePluginCouldNotSaveState = 30037 # Plugin could not save state (eg. no state directory)
    ePluginDoesNotSaveState = 30037 # Plugin does not support saving state
    ePluginDisabled = 30039 # Plugin is currently disabled
    eErrorCallingPluginRoutine = 30040 # Could not call plugin routine
    eCommandsNestedTooDeeply = 30041 # Calls to "Execute" nested too deeply
    eCannotCreateChatSocket = 30042 # Unable to create socket for chat connection
    eCannotLookupDomainName = 30043 # Unable to do DNS (domain name) lookup for chat connection
    eNoChatConnections = 30044 # No chat connections open
    eChatPersonNotFound = 30045 # Requested chat person not connected
    eBadParameter = 30046 # General problem with a parameter to a script call
    eChatAlreadyListening = 30047 # Already listening for incoming chats
    eChatIDNotFound = 30048 # Chat session with that ID not found
    eChatAlreadyConnected = 30049 # Already connected to that server/port
    eClipboardEmpty = 30050 # Cannot get (text from the) clipboard
    eFileNotFound = 30051 # Cannot open the specified file
    eAlreadyTransferringFile = 30052 # Already transferring a file
    eNotTransferringFile = 30053 # Not transferring a file
    eNoSuchCommand = 30054 # There is not a command of that name
    eArrayAlreadyExists = 30055 # That array already exists
    eArrayDoesNotExist = 30056 # That array does not exist
    eBadKeyName = 30056 # That name is not permitted for a key
    eArrayNotEvenNumberOfValues = 30057 # Values to be imported into array are not in pairs
    eImportedWithDuplicates = 30058 # Import succeeded, however some values were overwritten
    eBadDelimiter = 30059 # Import/export delimiter must be a single character, other than backslash
    eSetReplacingExistingValue = 30060 # Array element set, existing value overwritten
    eKeyDoesNotExist = 30061 # Array key does not exist
    eCannotImport = 30062 # Cannot import because cannot find unused temporary character
    eItemInUse = 30063 # Cannot delete trigger/alias/timer because it is executing a script
    eSpellCheckNotActive = 30064 # Spell checker is not active
    eCannotAddFont = 30065 # Cannot create requested font
    ePenStyleNotValid = 30066 # Invalid settings for pen parameter
    eUnableToLoadImage = 30067 # Bitmap image could not be loaded
    eImageNotInstalled = 30068 # Image has not been loaded into window
    eInvalidNumberOfPoints = 30069 # Number of points supplied is incorrect
    eInvalidPoint = 30070 # Point is not numeric
    eHotspotPluginChanged = 30071 # Hotspot processing must all be in same plugin
    eHotspotNotInstalled = 30072 # Hotspot has not been defined for this window
    eNoSuchWindow = 30073 # Requested miniwindow does not exist
    eBrushStyleNotValid = 30074 # Invalid settings for brush parameter

class SendTo:
    '''
    Trigger、Alias、Timer创建时的SendTo对应的常量定义
    '''
    World = 0 
    CommandWindow = 1
    OutputWindow = 2
    StatusLine = 3
    NotepadNew = 4
    NotepadAppend = 5
    LogFile = 6
    NotepadReplace = 7
    CommandQueue = 8
    Variable = 9
    Execute = 10 #re-parse as command
    Speedwalk = 11 #send text is speedwalk, queue it
    Script = 12 #send to script engine
    Immediate = 13 #send to world in front of speedwalk queue
    ScriptAfterOmit = 14  #send to script engine, after lines have been omitted

class TriggerFlag:
    '''
    创建Trigger所需的Flags 
    '''
    Enabled = 1 # enable trigger 
    OmitFromLog = 2 # omit from log file 
    OmitFromOutput = 4 # omit trigger from output 
    KeepEvaluating = 8 # keep evaluating 
    IgnoreCase = 16 # ignore case when matching 
    TriggerRegularExpression = 32 # trigger uses regular expression 
    ExpandVariables = 512 # expand variables like @direction 
    Replace = 1024 # replace existing trigger of same name 
    LowercaseWildcard = 2048 # wildcards forced to lower-case
    Temporary = 16384 # temporary - do not save to world file 
    OneShot = 32768
    ReplaceTemporaryRegular = Replace | TriggerRegularExpression | Temporary
    ReplaceTemporaryRegularEnabled = ReplaceTemporaryRegular | Enabled
    ReplaceTemporaryRegularKeep = KeepEvaluating | ReplaceTemporaryRegular
    ReplaceTemporaryRegularKeepEnabled = ReplaceTemporaryRegularKeep | Enabled
    ReplaceTemporaryOneShotEnabled = OneShot + Temporary + Replace + Enabled
    
class Colors:
    '''
    创建Trigger所需的Colours 
    '''
    NOCHANGE = -1
    Custom1 = 0
    Custom2 = 1
    Custom3 = 2 
    Custom4 = 3
    Custom5 = 4
    Custom6 = 5
    Custom7 = 6
    Custom8 = 7
    Custom9 = 8
    Custom10 = 9
    Custom11 = 10
    Custom12 = 11
    Custom13 = 12
    Custom14 = 13
    Custom15 = 14
    Custom16 = 15

class AliasFlag:
    '''
    创建Alias所需的Flags 
    '''
    Enabled = 1 # same as for AddTrigger 
    KeepEvaluating = 8
    IgnoreAliasCase = 32 # ignore case when matching 
    OmitFromLogFile = 64 # omit this alias from the log file 
    AliasRegularExpression = 128 # alias is regular expressions 
    ExpandVariables = 512 # same as for AddTrigger 
    Replace = 1024 # same as for AddTrigger 
    AliasSpeedWalk = 2048 # interpret send string as a speed walk string 
    AliasQueue = 4096 # queue this alias for sending at the speedwalking delay interval 
    AliasMenu = 8192 # this alias appears on the alias menu 
    Temporary = 16384 # same as for AddTrigger
    ReplaceTemporaryExpandRegularEnabled = Replace | ExpandVariables | AliasRegularExpression | Enabled


class TimerFlag:
    '''
    创建Timer所需的Flags 
    '''
    Enabled = 1 # same as for AddTrigger
    AtTime = 2 # if not set, time is "every" 
    OneShot = 4 # if set, timer only fires once 
    TimerSpeedWalk = 8 # timer does a speed walk when it fires 
    TimerNote = 16 # timer does a world.note when it fires 
    ActiveWhenClosed = 32  # timer fires even when world is disconnected
    Replace = 1024 # same as for AddTrigger
    Temporary = 16384 # same as for AddTrigger
    ReplaceTemporary = Temporary | Replace
    ReplaceTemporaryEnabled = ReplaceTemporary | Enabled