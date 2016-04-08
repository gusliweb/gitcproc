import sys
import re

sys.path.append("../util")

import Util
import UnsupportedLanguageException
import
from chunkingConstants import *
from scopeTracker import *

#Scope Tracking in Python
#Can not mix Tabs and WhiteSpaces
#Indent level not specific


#Redo with a polymorphic solution for the languages
class PythonScopeTracker(scopeTracker):
    def __init__(self, language):
        #These are pseudo stacks implemented as lists that track the current 
        #number of open scopes (brackets, tabs, etc), each change gets its own
        #entry, which is then deleted when we see a matching closing entry
        #Functions and blocks are included in full so they can be matched later
        self.oldVerStack = []
        self.newVerStack = []
        self.indentToken = "" #This tells us what the indent token for the file is.  Can be a number of spaces or tab
        self.lastNewContext = ""
        self.lastNewContextType = NULL #Used to identify if the previous line was the start of a group or function scope.
        self.lastOldContext = ""
        self.lastOldContextType = NULL #Used to identify if the previous line was the start of a group or function scope.
        self.lastOldFuncContext = ""
        self.lastOldBlockContext = []
        self.lastNewFuncContext = ""
        self.lastNewBlockContext = []
        self.language = language

    #String -> list
    #Returns a list giving the sequence of scope changes in this line.
    def scopeOrder(self, line, lineType):
        if(self.isScopeIncrease(line,lineType)):
            return [INCREASE]
        elif(self.isScopeDecrease(line,lineType)):
            return [DECREASE]
        else:
            return []
        
    def scopeIncreaseCount(self, line, lineType):
        if(self.isScopeIncrease(line,lineType)):
            return 1
        else:
            return 0

    def scopeDecreaseCount(self, line, lineType):
        if(self.isScopeDecrease(line, lineType)):
            return 1
        else:
            return 0

    def indentDepth(self, whiteSpace):
        #Make sure there is no mixing of tabs and spaces
        #if(Util.DEBUG):
        #    try:
        #        print("Indent Token: \"" + self.indentToken + "\"")
        #        print("WhiteSpace: \"" + whiteSpace + "\"")
        #    except:
        #        print("Indent Token: \"" + unicode(self.indentToken, 'utf-8', errors='ignore') + "\"")
        #        print("WhiteSpace: \"" + unicode(whiteSpace, 'utf-8', errors='ignore') + "\"")

        assert(self.indentToken != "")
        if(self.indentToken == "\t"):
            assert(" " not in whiteSpace)
        else:
            assert("\t" not in whiteSpace)

        return len(re.findall(self.indentToken, whiteSpace))

    #Returns true if this line contains an increased level of scope.
    #One possible concern here is a single statement spread over multiple lines.  I don't think that would cause
    #issues if we treat them like any other indent, but it could be a problem.
    def isScopeIncrease(self, line, lineType):
        #Match beginning whitespace.  Credit to kennytm here: 
        #http://stackoverflow.com/questions/2268532/grab-a-lines-whitespace-indention-with-python
        indent = re.match(r"\s*", line).group() 
        if(indent != ""):
            if(self.indentToken == ""): #Is this the first indent in the file?  Use this to determine future indentation
                self.indentToken = indent
                return True
            else:
                #How deep is the indent?
                depth = self.indentDepth(indent)
                if(lineType == ADD):
                    return len(self.newVerStack) < depth
                elif(lineType == REMOVE):
                    return len(self.oldVerStack) < depth
                elif(lineType == OTHER): #Can these be different?
                    return len(self.oldVerStack) < depth or len(self.newVerStack) < depth #If these are different, just adjust the stack accordingly
                else:
                    assert("Not a valid line type")
        else:
            return False


    #Returns true if this line contains an decreased level of scope.
    def isScopeDecrease(self, line, lineType):
        assert(self.indentToken != "") #If Scope is decreasing, if must have increased at some point
        indent = re.match(r"\s*", line).group() 
        depth = self.indentDepth(indent)
        if(lineType == ADD):
            return len(self.newVerStack) > depth
        elif(lineType == REMOVE):
            return len(self.oldVerStack) > depth
        elif(lineType == OTHER): #Can these be different?
            return len(self.oldVerStack) > depth or len(self.newVerStack) > depth #If these are different, just adjust the stack accordingly
        else:
            assert("Not a valid line type")

    def handleFunctionNameEnding(self, line, functionName):
        #Our job here is to distinguish between a indented line with a function def
        #and the indented line following the function.
        if("def " in line):
        #    functionName += line.split(":")[0] + ":"


        return functionName

    #Private function to update the stack for the shift at the next 
    def updateStack(self, changeType, stack, contextType, context, line):
        if(changeType == FUNC): #This is an indented function, the actual function indent must come later
            contextType == FUNC
            context = line
            stack.append((self.indentToken, GENERIC)) #Should be able to increase only 1 level at a time?
        elif(changeType == SBLOCK):
            contextType == SBLOCK
            context = line
            stack.append((self.indentToken, GENERIC)) #Should be able to increase only 1 level at a time?
        elif(changeType == NULL): #Reset the values, don't update the stack.
            contextType == NULL
            context = ""
        elif(changeType == GENERIC):
            stack.append((self.indentToken, GENERIC)) #Should be able to increase only 1 level at a time?
        else:
            assert("Not a valid change type.")

        
        return (stack, contextType, context)

    def increaseNewIndent(self, line, changeType, lineDiff):
        if(Util.DEBUG):
            print("Adding: " + str(line))
            print("Type: " + str(changeType))
            print("Stack: " + str(self.newVerStack))

        # #If we haven't seen a scope increase yet, what is causing the scope change
        # if(self.lastContextType == NULL):
        #     (self.newVerStack, self.lastNewContextType, self.lastNewContext) = updateStack(changeType, self.newVerStack, self.lastNewContextType, self.lastNewContext, line)

        # elif(self.lastContextType == GENERIC):
        # elif(self.lastContextType == FUNC):
        #     self.oldVerStack.append((self.lastNewContext, FUNC))
        #     self.lastOldFuncContext = line
        #     (self.newVerStack, self.lastNewContextType, self.lastNewContext) = updateStack(changeType, self.newVerStack, self.lastNewContextType, self.lastNewContext, line)
        # elif(self.lastContextType == SBLOCK):
        # else:
        #     assert("Not a valid change type.")


        if(changeType == GENERIC):
            self.oldVerStack.append((self.indentToken, GENERIC)) #Should be able to increase only 1 level at a time?
        elif(changeType == FUNC):
            #Mark that we've seen the function...          
            self.newVerStack.append((line, FUNC))
            self.lastNewFuncContext = line
        elif(changeType == SBLOCK):
            if(lineDiff == 0): #This is not the indent for the Block, but a Block keyword that is indented
                #TODO
            elif(lineDiff == 1):
                self.newVerStack.append((line, SBLOCK))
                self.lastNewBlockContext.append(line)
        else:
            assert("Not a valid change type.")

        if(Util.DEBUG):
            print("Stack (After): " + str(self.newVerStack))

    def increaseOldIndent(self, line, changeType, lineDiff):
        if(Util.DEBUG):
            print("Adding: " + str(line))
            print("Type: " + str(changeType))
            print("Stack: " + str(self.oldVerStack))
        if(changeType == GENERIC):
            self.oldVerStack.append((self.indentToken, GENERIC)) #Should be able to increase only 1 level at a time?
        elif(changeType == FUNC):
            self.oldVerStack.append((line, FUNC))
            self.lastOldFuncContext = line
        elif(changeType == SBLOCK):
            self.oldVerStack.append((line, SBLOCK))
            self.lastOldBlockContext.append(line)
        else:
            assert("Not a valid change type.")

        if(Util.DEBUG):
            print("Stack (After): " + str(self.oldVerStack))

    #string, [ADD|REMOVE|OTHER], [GENERIC|FUNC|BLOCK] -> --
    #Increase the depth of our tracker and add in function or block contexts if they have been discovered.
    def increaseScope(self, line, lineType, changeType, lineDiff):
        if(Util.DEBUG):
            try:
                print("Scope Increasing Line: " + line)
            except:
                print("Scope Increasing Line: " + unicode(line, 'utf-8', errors='ignore'))

        if(lineType == ADD):
            self.increaseNewIndent(line, changeType, lineDiff)
        elif(lineType == REMOVE):
            self.increaseOldIndent(line, changeType, lineDiff)
        elif(lineType == OTHER): 
            #TODO: How do I handle this now.
            #If increase relative to old th
            depth = self.indentDepth(line)
            isOldIncrease = len(self.oldVerStack) < depth
            isNewIncrease = len(self.newVerStack) < depth
            assert(isOldIncrease or isNewIncrease)
            if(isOldIncrease):
                self.increaseOldIndent(line, changeType, lineDiff)
            if(isNewIncrease):
                self.increaseNewIndent(line, changeType, lineDiff)
        else:
            assert("Not a valid line type")


    #Remove indents from the new stack and update the functional and block caches accordingly
    def decreaseNewIndent(self, line):
        if(self.newVerStack != []):
            removed = self.newVerStack.pop()
            if(Util.DEBUG):
                print("Removing: " + str(removed))
                print("Context: " + str(self.lastNewBlockContext))
                print("Stack: " + str(self.newVerStack))
            if(removed[LABELINDEX] == FUNC):
                self.lastNewFuncContext = self.getTopType(self.newVerStack, FUNC)
            elif(removed[LABELINDEX] == SBLOCK):
                self.lastNewBlockContext.remove(removed[LINEINDEX])
        else:#Bracket overclosing -> estimating...
            if(Util.DEBUG):
                print("Popped from empty new Stack.")

    #Remove indents from the old stack and update the functional and block caches accordingly
    def decreaseOldIndent(self, line):
        if(self.oldVerStack != []):
            removed = self.oldVerStack.pop()
            if(Util.DEBUG):
                print("Removing: " + str(removed))
                print("Context: " + str(self.lastOldBlockContext))
                print("Stack: " + str(self.oldVerStack))
            if(removed[LABELINDEX] == FUNC):
                self.lastOldFuncContext = self.getTopType(self.oldVerStack, FUNC)
            elif(removed[LABELINDEX] == SBLOCK):
                self.lastOldBlockContext.remove(removed[LINEINDEX])
        else:#Bracket overclosing -> estimating...
            if(Util.DEBUG):
                print("Popped from empty old Stack.")

    #string, [ADD|REMOVE|OTHER] -> --
    #Decrease our current scope and close out any function or block contexts if necessary.
    def decreaseScope(self, line, lineType):
        if(lineType == ADD):
            self.decreaseNewIndent(line)
        elif(lineType == REMOVE):
            self.decreaseOldIndent(line)
        elif(lineType == OTHER): 
            #TODO: How do I handle this now.
            #If increase relative to old th
            depth = self.indentDepth(line)
            isOldDecrease = len(self.oldVerStack) > depth
            isNewDecrease = len(self.newVerStack) > depth
            assert(isOldDecrease or isNewDecrease)
            if(isOldDecrease):
                self.decreaseOldIndent(line)
            if(isNewDecrease):
                self.decreaseNewIndent(line)
        else:
            assert("Not a valid line type")