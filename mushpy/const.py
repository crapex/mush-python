# -*- coding:utf-8 -*-

# mushclient中常用的常量定义

class Returns:
    '''
    各类返回值常量定义
    '''
    OK = 0 # No error
    WorldOpen = 30001 # The world is already open
    WorldClosed = 30002 # The world is closed, this action cannot be performed
    NoNameSpecified = 30003 # No name has been specified where one is required
    CannotPlaySound = 30004 # The sound file could not be played
    TriggerNotFound = 30005 # The specified trigger name does not exist
    TriggerAlreadyExists = 30006 # Attempt to add a trigger that already exists
    TriggerCannotBeEmpty = 30007 # The trigger "match" string cannot be empty
    InvalidObjectLabel = 30008 # The name of this object is invalid
    ScriptNameNotLocated = 30009 # Script name is not in the script file
    AliasNotFound = 30010 # The specified alias name does not exist
    AliasAlreadyExists = 30011 # Attempt to add a alias that already exists
    AliasCannotBeEmpty = 30012 # The alias "match" string cannot be empty
    CouldNotOpenFile = 30013 # Unable to open requested file
    LogFileNotOpen = 30014 # Log file was not open
    LogFileAlreadyOpen = 30015 # Log file was already open
    LogFileBadWrite = 30016 # Bad write to log file
    TimerNotFound = 30017 # The specified timer name does not exist
    TimerAlreadyExists = 30018 # Attempt to add a timer that already exists
    VariableNotFound = 30019 # Attempt to delete a variable that does not exist
    CommandNotEmpty = 30020 # Attempt to use SetCommand with a non-empty command window
    BadRegularExpression = 30021 # Bad regular expression syntax
    TimeInvalid = 30022 # Time given to AddTimer is invalid
    BadMapItem = 30023 # Direction given to AddToMapper is invalid
    NoMapItems = 30024 # No items in mapper
    UnknownOption = 30025 # Option name not found
    OptionOutOfRange = 30026 # New value for option is out of range
    TriggerSequenceOutOfRange = 30027 # Trigger sequence value invalid
    TriggerSendToInvalid = 30028 # Where to send trigger text to is invalid
    TriggerLabelNotSpecified = 30029 # Trigger label not specified/invalid for 'send to variable'
    PluginFileNotFound = 30030 # File name specified for plugin not found
    ProblemsLoadingPlugin = 30031 # There was a parsing or other problem loading the plugin
    PluginCannotSetOption = 30032 # Plugin is not allowed to set this option
    PluginCannotGetOption = 30033 # Plugin is not allowed to get this option
    NoSuchPlugin = 30034 # Requested plugin is not installed
    NotAPlugin = 30035 # Only a plugin can do this
    NoSuchRoutine = 30036 # Plugin does not support that subroutine (subroutine not in script)
    PluginDoesNotSaveState = 30037 # Plugin does not support saving state
    PluginCouldNotSaveState = 30037 # Plugin could not save state (eg. no state directory)
    PluginDisabled = 30039 # Plugin is currently disabled
    ErrorCallingPluginRoutine = 30040 # Could not call plugin routine
    CommandsNestedTooDeeply = 30041 # Calls to "Execute" nested too deeply
    CannotCreateChatSocket = 30042 # Unable to create socket for chat connection
    CannotLookupDomainName = 30043 # Unable to do DNS (domain name) lookup for chat connection
    NoChatConnections = 30044 # No chat connections open
    ChatPersonNotFound = 30045 # Requested chat person not connected
    BadParameter = 30046 # General problem with a parameter to a script call
    ChatAlreadyListening = 30047 # Already listening for incoming chats
    ChatIDNotFound = 30048 # Chat session with that ID not found
    ChatAlreadyConnected = 30049 # Already connected to that server/port
    ClipboardEmpty = 30050 # Cannot get (text from the) clipboard
    FileNotFound = 30051 # Cannot open the specified file
    AlreadyTransferringFile = 30052 # Already transferring a file
    NotTransferringFile = 30053 # Not transferring a file
    NoSuchCommand = 30054 # There is not a command of that name
    ArrayAlreadyExists = 30055 # That array already exists
    BadKeyName = 30056 # That name is not permitted for a key
    ArrayDoesNotExist = 30056 # That array does not exist
    ArrayNotEvenNumberOfValues = 30057 # Values to be imported into array are not in pairs
    ImportedWithDuplicates = 30058 # Import succeeded, however some values were overwritten
    BadDelimiter = 30059 # Import/export delimiter must be a single character, other than backslash
    SetReplacingExistingValue = 30060 # Array element set, existing value overwritten
    KeyDoesNotExist = 30061 # Array key does not exist
    CannotImport = 30062 # Cannot import because cannot find unused temporary character

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