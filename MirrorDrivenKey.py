import maya.cmds as cmds

# Global Functions
def findOutputs():
    curves = cmds.ls(type = ('animCurveUL'))

    items = []
    for c in curves:
        driving = cmds.listConnections(c + '.input', p = 1)
        futureNodes = [node for node in cmds.listHistory(c, future=1, ac=1)]
        futureNodes.reverse()
        drivenAttr = None
        for node in futureNodes:
            
            if cmds.nodeType(node) == 'unitConversion':
                try:
                    drivenAttr = cmds.listConnections(node + '.output', p=1)[0]
                    break
                except:
                    cmds.warning('blendWeighted node with no output: ' + node)
                    break
            elif cmds.nodeType(node) == 'blendWeighted':
                try:
                    drivenAttr = cmds.listConnections(node + '.output', p=1)[0]
                    break
                except:
                    cmds.warning('blendWeighted node with no output: ' + node)
                    break
        if not drivenAttr:

            drivenAttr = cmds.listConnections(c , p=1)[0]
        if drivenAttr:
            drivenAttr2 = drivenAttr
        else:
            cmds.warning('No driven attr found for ' + c)
        #print driving
        if driving != None:
                
            items.append([driving[0], drivenAttr2])
        
    
    return items

def modifyNodeName(test=''):
    test = test.split('_')
    output = ''
    for i in range(len(test) - 2):
        output = output + test[i] + '_'
        
    output = output + test[-2] + '.' + test[-1]
    return output
    
def findDrivenKey(name = '', old = '', new = ''):
    
    transformed_list = []
    transformed_list_father = []
    transformed_list_child = []
    test_list = []
    missing_list = []
    
    drivenKeyRelationship = findOutputs()
    for output in drivenKeyRelationship:
        if output[0] == name:
            transformed_list.append(output[1])
    for i in transformed_list:
        if (old in i) == False:
            missing_list.append(i)            
            #return False
        else:
            transformed_list_father.append(i)
            transformed_list_child.append(i.replace(old, new))
    if len(missing_list)!=0:
        print 'Unable to find keywords in name of driven key items'
        percentage = str(round(float(len(transformed_list) - len(missing_list))/float(len(transformed_list)) * 100))
        count = str(len(missing_list))
        missing_list = '\n'.join(map(str, missing_list))
        cmds.confirmDialog( title='Keyword missing', message='Due to the given keyword, '+percentage+'% completed, and '+count+
        ' driven node(s) are skipped. They are: \n ' + missing_list, button=['OK'], defaultButton='OK')
    return [transformed_list_father,transformed_list_child, missing_list]
     
# Input 1: name of channel, Input2: name of target
def copyDrivenKeyAttr(father_list = [], children_list = [], missing_list = [], father_driver_list='', children_driver_list = '', flag = 0):
    #print father_list
    #declare a list that store missing driven item
    lostList = []
    if (len(father_list) == 0 and len(missing_list) == 0):
        print 'No driven keys on this driver key attribute, try another one pls'#####################
        cmds.confirmDialog( title='Failed to find driven key', message='No driven keys on this source driver, try another one.', button=['OK'], defaultButton='OK')
        return

    for i in children_list:
        exist = cmds.objExists(i)
        
        if not exist:
            lostList.append(i)
    if (len(lostList) == 0):
         
        for i in range(len(father_list)):
            # Preprocess string format
            # Transform the last character into capital
            
            #father_change_list = list(father_list[i])
            father_change_list = father_list[i]
            #father_change_list[-1] = father_change_list[-1].upper() 
            father_list[i] = ''.join(father_change_list)

            #children_change_list = list(children_list[i])
            
            children_change_list  = children_list[i]
            #children_change_list[-1] = children_change_list[-1].upper()
            children_list[i] = ''.join(children_change_list)
        
        
            father_driver_string_list = father_driver_list.split('.')
            children_driver_string_list = children_driver_list.split('.')
            #print children_driver_list
            try:
                dataType = cmds.getAttr(children_driver_list, type= True )
                #dataType = str(dataType)
                if dataType != 'double':
                    cmds.confirmDialog( title='Invalid target driver', message='The version of this tool is only work for decimal number type attribute, example: 0.5, 1.0, 3.1415926', button=['OK'], defaultButton='OK')
                    return
            except:
                cmds.confirmDialog( title='Invalid target driver', message='You seemed select the wrong name.', button=['OK'], defaultButton='OK')
                return
            
            
        
            #MindrivenAttr
            minExist_f = cmds.attributeQuery(father_driver_string_list[1], node = father_driver_string_list[0], mne = True)
            minExist_c = cmds.attributeQuery(children_driver_string_list[1], node = children_driver_string_list[0], mne = True)

            if (minExist_f is True) and (minExist_c is True):
                cmds.setAttr(father_driver_list, 0)
                cmds.setAttr(children_driver_list, 0)
                cmds.setAttr(children_list[i], cmds.getAttr(father_list[i]))
                cmds.setDrivenKeyframe(children_list[i], cd = children_driver_list)
                
                father_min = cmds.attributeQuery(father_driver_string_list[1], node = father_driver_string_list[0], min = True)
                children_min = cmds.attributeQuery(children_driver_string_list[1], node = children_driver_string_list[0], min = True)
                cmds.setAttr(father_driver_list, father_min[0])
                cmds.setAttr(children_driver_list, children_min[0])
        
                temp_list = children_list[i].split('.')
                if flag == True:
                    if (temp_list[1] == 'rotateY') or (temp_list[1] == 'translateX'):
                        cmds.setAttr(children_list[i], -cmds.getAttr(father_list[i]))
                    else:
                        cmds.setAttr(children_list[i], cmds.getAttr(father_list[i]))
                else:
                    cmds.setAttr(children_list[i], cmds.getAttr(father_list[i]))
                cmds.setDrivenKeyframe(children_list[i], cd = children_driver_list)
                
            elif minExist_f is False:
                cmds.confirmDialog( title='No min value', message='There is no min value on source driver attribute, please set up a minimum value.', button=['OK'], defaultButton='OK')
                print 'Bad inputs in Min_F, no min value'##########################
                return
            else:
                cmds.confirmDialog( title='No min value', message='There is no min value on target driver attribute, please set up a minimum value.', button=['OK'], defaultButton='OK')
                print 'Bad inputs in Min_C, no min value'##########################
                return
        
            #Max
            maxExist_f = cmds.attributeQuery(father_driver_string_list[1], node = father_driver_string_list[0], mxe = True)
            maxExist_c = cmds.attributeQuery(children_driver_string_list[1], node = children_driver_string_list[0], mxe = True)
        
            if (maxExist_f is True) and (maxExist_c is True):
                father_max = cmds.attributeQuery(father_driver_string_list[1], node = father_driver_string_list[0], max = True)
                children_max = cmds.attributeQuery(children_driver_string_list[1], node = children_driver_string_list[0], max = True)
                cmds.setAttr(father_driver_list, father_max[0])
                cmds.setAttr(children_driver_list, children_max[0])
        
                temp_list = children_list[i].split('.')
                if flag == True:
                    if (temp_list[1] == 'rotateY') or (temp_list[1] == 'translateX'):
                        cmds.setAttr(children_list[i], -cmds.getAttr(father_list[i]))
                    else:
                        cmds.setAttr(children_list[i], cmds.getAttr(father_list[i]))
                else:
                    cmds.setAttr(children_list[i], cmds.getAttr(father_list[i]))
                cmds.setDrivenKeyframe(children_list[i], cd = children_driver_list)
                
            elif maxExist_f is False:
                cmds.confirmDialog( title='No max value', message='There is no max value on source driver attribute, please set up a maximum value.', button=['OK'], defaultButton='OK')
                print 'Bad inputs in Max_F, no max value'##########################
                return
            else:
                cmds.confirmDialog( title='No max value', message='There is no max value on target driver attribute, please set up a maximum value.', button=['OK'], defaultButton='OK')
                print 'Bad inputs in Max_C, no max value'##########################
                return
                    
            cmds.setAttr(father_driver_list, 0)
            cmds.setAttr(children_driver_list, 0)
            
        return 'Success'
            
        #cmds.confirmDialog( title='Mirror Result', message='=====================Mirror Has Done.=======================', button=['OK'], defaultButton='OK')
    else:
        print 'Mirror failed, missing nodes:'
        lost = ''
        for i in lostList:
            lost += i + ', '
        lostList = '\n'.join(map(str, lostList))
        cmds.confirmDialog( title='Mirror Failed', message='Mirror failed, missing nodes: \n' + lostList, button=['OK'], defaultButton='OK')


#Windows function
class OptionsWindow(object):
    @classmethod
    def showUI(cls):
        win = cls()
        win.create()
        return win
    def __init__(self):
        self.window = 'Options Window'
        self.title = 'Mirror Driven Key Tool'
        self.heightwidth = (400,546)
        self.supportsToolAction = False
        self.actionName = 'Apply and Close'
    def create(self):
        if (cmds.window(self.window, exists=True)):
            cmds.deleteUI(self.window, window=True)
        self.window = cmds.window(
            self.window,
            title = self.title,
            widthHeight = self.heightwidth,
            menuBar = True
        )
        self.commonMenuBar()
        
        self.mainForm = cmds.formLayout(nd=100)
        
        self.texthint = cmds.text('   Use buttons below to load mirror source and target controllers : ')
        
        self.buttonhint = cmds.button(
                          label = '?',
                          height = 15,
                          width = 15,
                          c = self.loadHint
        )
        
        cmds.formLayout(self.mainForm, e = True, attachControl = [self.buttonhint, 'left', 5, self.texthint])
        
        self.commonButtons()

        cmds.formLayout(self.mainForm, e = True, attachControl = [self.loadDriver, 'top', 5, self.texthint])
        cmds.formLayout(self.mainForm, e = True, attachControl = [self.loadDriven, 'top', 5, self.texthint])
        
        self.myoutliner = cmds.nodeOutliner(so = True, ms = False, addCommand='print("%node \\n")' )
        self.myoutliner2 = cmds.nodeOutliner(so = True, ms = False, addCommand='print("%node \\n")' )
        
        cmds.formLayout( self.mainForm, edit=True, 
            attachForm=((self.myoutliner, 'left', 5), 
                        (self.myoutliner2, 'right', 5),
                        (self.myoutliner, 'bottom', 150),
                        (self.myoutliner2, 'bottom', 150)),
            attachControl=((self.myoutliner, 'right', 5, self.myoutliner2),
                           (self.myoutliner, 'top', 10, self.loadDriver),
                           (self.myoutliner2, 'top', 10, self.loadDriven)),
            attachPosition=(self.myoutliner2,'left', 0, 50))
        
        self.boarderOptions = cmds.tabLayout(
            scrollable = True,
            height = 1,
            tabsVisible = False
        )
        cmds.formLayout(
            self.mainForm, e=True,
            attachForm = (
                [self.boarderOptions, 'left', 4],
                [self.boarderOptions, 'right', 4]
                
            ),
            attachControl = (
                [self.boarderOptions, 'top', 10, self.myoutliner],
                [self.boarderOptions, 'bottom', 4, self.applyBtn]
            )
        )
        self.optionsForm = cmds.formLayout(nd=100)
        
        self.displayOptions()
        
        cmds.showWindow()
        
    def commonMenuBar(self, *args):
        self.editMenu = cmds.menu(
            label = 'Edit'
        )

        self.editMenuReset = cmds.menuItem(
            label = 'Reset Settings',
            command = self.editMenuResetCmd
        )
        
        self.helpMenu = cmds.menu(
            label = 'Help'
        )
        
        self.helpMenuItem = cmds.menuItem(
            label = 'Help on %s'%self.title,
            command = self.helpMenuItemCmd
        )
        
    def editMenuResetCmd(self, *args):
        cmds.nodeOutliner(self.myoutliner, e = True, removeAll = True)
        cmds.nodeOutliner(self.myoutliner2, e = True, removeAll = True)
        cmds.textField(self.src, e = True, text = '')
        cmds.textField(self.des, e = True, text = '')

    def helpMenuItemCmd(self, *args):
        cmds.launch(web = 'http://yunhaohuofiea.blogspot.com/2017/04/maya-mirror-driven-key-tool-guide.html')
        
    def commonButtons(self, *args):
        self.commonBtnSize = ((self.heightwidth[0]-18)/3,26)
        self.loadDriver = cmds.button(
            label = 'Load Source Controller',
            height = self.commonBtnSize[1],
            command = self.loadDriverCmd
        )
        self.loadDriven = cmds.button(
            label = 'Load Target Controller',
            height = self.commonBtnSize[1],
            command = self.loadDrivenCmd
        )
        self.actionBtn = cmds.button(
            label = self.actionName,
            height = self.commonBtnSize[1],
            command = self.actionBtnCmd
        )
        self.applyBtn = cmds.button(
            label = 'Apply',
            height = self.commonBtnSize[1],
            command = self.applyBtnCmd
        )
        self.closeBtn = cmds.button(
            label = 'Close',
            height = self.commonBtnSize[1],
            command = self.closeBtnCmd
        )
        
        cmds.formLayout(
            self.mainForm, e=True,
            attachForm = (
                [self.actionBtn, 'left',3],
                [self.actionBtn, 'bottom',3],
                [self.applyBtn, 'bottom',3],
                [self.closeBtn, 'bottom',3],
                [self.closeBtn, 'right',3],
                [self.loadDriver, 'top', 5],
                [self.loadDriven, 'top', 5],
                [self.loadDriver, 'left', 5],
                [self.loadDriven, 'right', 5]
            ),
            attachControl = (
                [self.applyBtn, 'left',3,self.actionBtn],
                [self.applyBtn, 'right',3,self.closeBtn],
                [self.loadDriver, 'right',5,self.loadDriven],
            ),
            attachPosition = (
                [self.actionBtn,'right',0,33],
                [self.closeBtn,'left',1,67],
                [self.loadDriven, 'left', 0, 50]
            )  
        )
    
    def loadHint(self, *args):
        value = cmds.confirmDialog(title='Load Driver Help', message='Follow procedures below to load your driven key source controller and target controller:'+
        '\n                                                                                                                                           '+
        '                             '+
        '1. In your viewport, select a controller whose attribute has driven keys connections.'+
        ' (the final controller will be chosen if multiple are selected).'+
        '\n                                                                                                         '+
        '                                                              2. Then click on Load Source Contriller button.'+
        '\n                                                                                                         '+
        '                                                              3. Select a controller you want to set(mirror) driven key on'+
        ', this controller should has the attribute that you want to set driven key on.                                                                '+
        '\n                                                                                                                                            '+
        '                        '+
        '4. Click on Load Target Driver button. '+'                                                                                                    '+
        '\n                                                                                                                                            '+
        '                        '+
        '5. Finally, select attribute with driven keys on left side, and target attribute on right side.' +
        '\n                                                                                                                                            '+
        '                        '+
        'NOTICE: Attribute with driven keys should has min and max value!', button=['OK','Tutorial'], ds='Tutorial', defaultButton='OK')
        if value == 'Tutorial':
            cmds.launch(web = 'http://yunhaohuofiea.blogspot.com/2017/04/maya-mirror-driven-key-tool-guide.html')
   
    def loadHint2(self, *args):
        value = cmds.confirmDialog(title='Type in Keyword Help', message=
        'Make sure the attribute you selected in the left node outliner above should drive or animate other geometry'+
        '\n                                                                                                                                            '+
        '                       '+
        
        'The keyword you type in the first line will be replaced by the input of second line to form a new names, and program will use them to navigagte to the right geometries.'+
        '\n                                                                                                                                            '+
        '                       '+
        'For example, the attribute you choose in the left node outliner above can drive two geometries named by "eye_l_", "ear_l_"'+
        '\n                                                                                                                                            '+
        '                       '+
        'Type in "_l_" in the first line, and "_r_" in the second line'+
        '\n                                                                                                                                            '+
        '                       '+
        'The result of this example will be: "eye_r", "ear_r_" in the scene will be animated by the attibute you choose in the right node outliner above.'
        , button=['OK','Tutorial'], ds = 'Tutorial', defaultButton='OK')
        if value == 'Tutorial':
            cmds.launch(web = 'http://yunhaohuofiea.blogspot.com/2017/04/maya-mirror-driven-key-tool-guide.html')
        
    def loadDriverCmd(self, *args):
        select_list = cmds.ls(sl = True)
        try:
            cmds.nodeOutliner( self.myoutliner, e=True, a=select_list[-1] )
        except:
            cmds.confirmDialog( title='No source driver', message='Please select source driver controller in view port and click Load Source Driver button. ', button=['OK'], defaultButton='OK')
            print 'No source controller object Selected!!!'

    def loadDrivenCmd(self, *args):
        select_list = cmds.ls(sl = True)
        try:
            cmds.nodeOutliner( self.myoutliner2, e=True, a=select_list[-1] )
        except:
            cmds.confirmDialog( title='No target driver', message='Please select target driver controller in view port and click Load Target Driver button. ', button=['OK'], defaultButton='OK')
            print 'No target controller object Selected!!!'
            
    def actionBtnCmd(self,*args):
        self.applyBtnCmd()
        self.closeBtnCmd()
      
    def applyBtnCmd(self,*args):
        #Making a progress bar
        self.progressWindow = cmds.window(title = 'Progress', widthHeight = (300, 50))#,tb = False
        cmds.columnLayout()
        self.progressControl = cmds.progressBar(maxValue = 10, width = 300)
        self.text = cmds.text(l = 'Start Progress...')
        cmds.progressBar(self.progressControl, edit=True, pr = 0)
        cmds.showWindow(self.progressWindow)
        
        self.selected = cmds.nodeOutliner(self.myoutliner, q = True, cs = True )
        self.selected2 = cmds.nodeOutliner(self.myoutliner2, q = True, cs = True )
        self.src_text = cmds.textField(self.src, q = True, text = True)
        self.des_text = cmds.textField(self.des, q = True, text = True )
        
        cmds.text(self.text, e = True, l = 'Processing your inputs...')
        cmds.progressBar(self.progressControl, edit=True, pr = 2)
        
        if self.selected == None or self.selected2 == None:
            cmds.deleteUI(self.progressWindow, window = True)
            cmds.confirmDialog( title='No attribute selected', message='Please select one attribute with driven keys in the left node outliner.', button=['OK'], defaultButton='OK')
            print 'Please select one attribute in the node outliner'
            return
        elif self.src_text == '' or self.des_text == '':
            cmds.deleteUI(self.progressWindow, window = True)
            cmds.confirmDialog( title='Missing replacement keywords', message='Please type in the replacements key words. ', button=['OK'], defaultButton='OK')
            print 'Please type in the replacements key words'
            return
        else:
            #Progress 30%
            cmds.text(self.text, e = True, l = 'Processing your inputs...')
            cmds.progressBar(self.progressControl, edit=True, pr = 3)
            flagM = cmds.radioButton(self.mirrorB, q = True, sl = True)
            #Progress 50%
            cmds.text(self.text, e = True, l = 'Finding Drivenkeys...')
            cmds.progressBar(self.progressControl, edit=True, pr = 5)
            resultList = findDrivenKey(self.selected[0], self.src_text, self.des_text) 
            if resultList == False:
                cmds.deleteUI(self.progressWindow, window = True)
                print 'Mirror failed.'   
                return
            # Progress 70%
            cmds.text(self.text, e = True, l = 'Processing valid attribute values, should take a while...')
            cmds.progressBar(self.progressControl, edit=True, pr = 7)
            result = copyDrivenKeyAttr(resultList[0], resultList[1], resultList[2], self.selected[0], self.selected2[0], flagM)
            cmds.text(self.text, e = True, l = 'Done.')
            cmds.progressBar(self.progressControl, edit=True, pr =10)
            cmds.deleteUI(self.progressWindow, window = True)
            if result == 'Success':
                cmds.confirmDialog( title='Mirror Result', message='=====================Mirror Has Done.=======================', button=['OK'], defaultButton='OK')
            else:
                pass
                
        
    def closeBtnCmd(self,*args):
        cmds.deleteUI(self.window, window = True)
        
    def displayOptions(self,*args):
        self.hint = cmds.text( label = '   Replacement names for mirror targets:')
        self.hint2 = cmds.button(
                     label = '?',
                     height = 15,
                     width = 15,
                     c = self.loadHint2
        )
        self.col = cmds.rowColumnLayout( numberOfColumns=2, cal = (2, 'center'), columnAttach=(1, 'right', 0), columnWidth=[(1, 100), (2, 250)] )
        cmds.formLayout(self.optionsForm, e = True, attachControl=[self.col, 'top', 0, self.hint])
        cmds.formLayout(self.optionsForm, e = True, attachControl=[self.hint2, 'left', 5, self.hint])
        cmds.text( label='Search For: ' )
        self.src = cmds.textField()
        cmds.text( label='Replace With: ' )
        self.des = cmds.textField()
        cmds.text( label='   ' )
        cmds.radioCollection()
        self.mirrorB = cmds.radioButton( 'Mirror Behavior', align = 'center', sl = True )
        cmds.text( label='   ' )
        self.mimicB = cmds.radioButton( 'Mimic Behavior', align = 'center', sl = False )

       
        
OptionsWindow.showUI()
        