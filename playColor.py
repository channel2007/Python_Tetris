# encoding: utf-8
import os, sys, random
import time
import pygame 
from pygame.locals import *
from drew import *

# 常數-磚塊快速下降速度.
BRICK_DROP_RAPIDLY   = 0.01
# 常數-磚塊正常下降速度.
BRICK_DOWN_SPEED_MAX = 0.5

# 視窗大小.
canvas_width = 800
canvas_height = 600

# 顏色.
color_block         = (0,0,0)
color_white         = (255, 255, 255)
color_red           = (255, 0, 0)
color_gray          = (107,130,114)
color_gray_block    = (20,31,23)
color_gray_green    = (0, 255, 0)
color_light_gray    = (200, 200, 200)

# ColorVer:
# 橘色   - N1.
box_color_orange    = (204,102,51)
# 紫色   - N2.
box_color_purple    = (153,102,153)
# 藍色   - L1.
box_color_blue      = (51,102,204)
# 紅色   - L2.
box_color_light_red = (204,51,51)
# 淡藍色 - T.
box_color_light_blue= (51,204,255)
# 黃色   - O.
box_color_yellow    = (204,204,51)
# 綠色   - I.
box_color_green     = (51,153,102)

# 定義磚塊.
brick_dict = {
    "10": ( 4, 8, 9,13), "11": ( 9,10,12,13),   # N1.
    "20": ( 5, 8, 9,12), "21": ( 8, 9,13,14),   # N2.
    "30": ( 8,12,13,14), "31": ( 4, 5, 8,12), "32": (8,  9, 10, 14), "33": (5,  9, 12, 13), # L1.
    "40": (10,12,13,14), "41": ( 4, 8,12,13), "42": (8,  9, 10, 12), "43": (4,  5,  9, 13), # L2.
    "50": ( 9,12,13,14), "51": ( 4, 8, 9,12), "52": (8,  9, 10, 13), "53": (5,  8,  9, 13), # T.
    "60": ( 8, 9,12,13),    # O.
    "70": (12,13,14,15), "71": ( 1, 5, 9,13)    #I.
}

# 方塊陣列(10x20).
bricks_array = []
for i in range(10):
    bricks_array.append([0]*20)
# 方塊陣列(4x4).
bricks = []
for i in range(4):
    bricks.append([0]*4)
# 下一個方塊陣列(4x4).
bricks_next = []
for i in range(4):
    bricks_next.append([0]*4)
# 下一個方塊圖形陣列(4x4).
bricks_next_object = []
for i in range(4):
    bricks_next_object.append([0]*4)    
# 磚塊數量串列.
bricks_list = []
for i in range(10):
    bricks_list.append([0]*20)

# 方塊在容器的位置.
# (-2~6)(  為6的時候不能旋轉方塊).
container_x = 3
# (-3~16)(-3表示在上邊界外慢慢往下掉).
container_y =-4

# 除錯訊息.
debug_message = False
# 判斷遊戲結束.
game_over = False

# 磚塊下降速度.
brick_down_speed = BRICK_DOWN_SPEED_MAX

# 方塊編號(1~7).
brick_id = 1
# 方塊狀態(0~3).
brick_state = 0

# 下一個磚塊編號(1~7).
brick_next_id = 1

# 最大連線數.
lines_number_max = 0
# 本場連線數.
lines_number = 0

# 遊戲狀態.
# 0:遊戲進行中.
# 1:清除磚塊.
game_mode = 0

#-------------------------------------------------------------------------
# 函數:秀字.
# 傳入:
#   text    : 字串.
#   x, y    : 坐標.
#   color   : 顏色.
#-------------------------------------------------------------------------
def showFont( text, x, y, color):
    global canvas    
    text = font.render(text, True, color) 
    canvas.blit( text, (x,y))

#-------------------------------------------------------------------------
# 函數:取得磚塊索引陣列.
# 傳入:
#   brickId : 方塊編號(1~7).
#   state   : 方塊狀態(0~3).
#-------------------------------------------------------------------------
def getBrickIndex( brickId, state):
    global brick_dict

    # 組合字串.
    brickKey = str(brickId)+str(state)
    # 回傳方塊陣列.
    return brick_dict[brickKey]

#-------------------------------------------------------------------------
# 轉換定義方塊到方塊陣列.
# 傳入:
#   brickId : 方塊編號(1~7).
#   state   : 方塊狀態(0~3).
#-------------------------------------------------------------------------
def transformToBricks( brickId, state):
    global bricks

    # 清除方塊陣列.
    for x in range(4):
        for y in range(4):
            bricks[x][y] = 0
     
    # 取得磚塊索引陣列.
    p_brick = getBrickIndex(brickId, state)
    
    # 轉換方塊到方塊陣列.
    for i in range(4):        
        bx = int(p_brick[i] % 4)
        by = int(p_brick[i] / 4)
        bricks[bx][by] = brickId

    """
    # 印出訊息.
    for y in range(4): 
        s = ""
        for x in range(4): 
            s = s + str(bricks[x][y]) + ","       
        print(s)
    """

#-------------------------------------------------------------------------
# 判斷是否可以複製到容器內.
# 傳出:
#   true    : 可以.
#   false   : 不可以.
#-------------------------------------------------------------------------
def ifCopyToBricksArray():
    global bricks, bricks_array
    global container_x, container_y

    posX = 0
    posY = 0
    for x in range(4):
        for y in range(4):
           if (bricks[x][y] != 0):
                posX = container_x + x
                posY = container_y + y
                if (posX >= 0 and posY >= 0):
                    try:
                        if (bricks_array[posX][posY] != 0):
                            return False
                    except:
                        return False
    return True

#-------------------------------------------------------------------------
# 複製方塊到容器內.
#-------------------------------------------------------------------------
def copyToBricksArray():
    global bricks, bricks_array
    global container_x, container_y
    
    posX = 0
    posY = 0
    for x in range(4):
        for y in range(4):
            if (bricks[x][y] != 0):
                posX = container_x + x
                posY = container_y + y
                if (posX >= 0 and posY >= 0):
                    bricks_array[posX][posY] = bricks[x][y]
     
#-------------------------------------------------------------------------
# 初始遊戲.
#-------------------------------------------------------------------------
def resetGame():
    global BRICK_DOWN_SPEED_MAX
    global bricks_array, bricks, lines_number, lines_number_max

    # 清除磚塊陣列.
    for x in range(10):
        for y in range(20):
            bricks_array[x][y] = 0
            
    # 清除方塊陣列.
    for x in range(4):
        for y in range(4):
            bricks[x][y] = 0

    # 初始磚塊下降速度.
    brick_down_speed = BRICK_DOWN_SPEED_MAX

    # 最大連線數.
    if(lines_number > lines_number_max):
        lines_number_max = lines_number
    # 連線數.
    lines_number = 0

#---------------------------------------------------------------------------
# 判斷與設定要清除的方塊.
# 傳出:
#   連線數
#---------------------------------------------------------------------------
def ifClearBrick():
    pointNum = 0
    lineNum = 0
    for y in range(20):
        for x in range(10):
            if (bricks_array[x][y] > 0):
                pointNum = pointNum + 1
            if (pointNum == 10):
                for i in range(10):
                    lineNum = lineNum + 1
                    bricks_array[i][y] = 9
        pointNum = 0
    return lineNum

#-------------------------------------------------------------------------
# 更新下一個磚塊.
#-------------------------------------------------------------------------
def updateNextBricks(brickId):
    global bricks_next
    
    # 清除方塊陣列.
    for y in range(4):
        for x in range(4):
            bricks_next[x][y] = 0

    # 取得磚塊索引陣列.
    pBrick = getBrickIndex(brickId, 0)

    # 轉換方塊到方塊陣列.
    for i in range(4):
        bx = int(pBrick[i] % 4)
        by = int(pBrick[i] / 4)
        bricks_next[bx][by] = brickId

    # ColorVer:設定背景顏色.
    background_bricks_next.color = color_block

    # 更新背景區塊.
    background_bricks_next.update()

    # 更新磚塊圖.
    pos_y = 52
    for y in range(4):
        pos_x = 592
        for x in range(4):
            if(bricks_next[x][y] != 0):
                bricks_next_object[x][y].rect[0] = pos_x
                bricks_next_object[x][y].rect[1] = pos_y

                # ColorVer:依照方塊編號設定顏色.
                if (bricks_next[x][y]==1):
                    bricks_next_object[x][y].color = box_color_orange
                elif (bricks_next[x][y]==2):
                    bricks_next_object[x][y].color = box_color_purple
                elif (bricks_next[x][y]==3):
                    bricks_next_object[x][y].color = box_color_blue
                elif (bricks_next[x][y]==4):
                    bricks_next_object[x][y].color = box_color_light_red
                elif (bricks_next[x][y]==5):
                    bricks_next_object[x][y].color = box_color_light_blue
                elif (bricks_next[x][y]==6):
                    bricks_next_object[x][y].color = box_color_yellow
                elif (bricks_next[x][y]==7):
                    bricks_next_object[x][y].color = box_color_green
                elif (bricks_next[x][y]==9):
                    bricks_next_object[x][y].color = color_white

                bricks_next_object[x][y].update()
            pos_x = pos_x + 28        
        pos_y = pos_y + 28
                
#-------------------------------------------------------------------------
# 產生新磚塊.
#-------------------------------------------------------------------------
def brickNew():
    global game_over, container_x, container_y, brick_id, brick_next_id, brick_state
    global lines_number, game_mode

    # 判斷遊戲結束.
    game_over = False
    if (container_y < 0):
        game_over = True

    # 複製方塊到容器內.
    container_y = container_y - 1
    copyToBricksArray()  
    
    #------------------------------------------------    
    # 判斷與設定要清除的方塊.
    lines = ifClearBrick() / 10;        
    if (lines > 0):
        # 消除連線數量累加.
        lines_number =  lines_number + lines
        # 修改連線數量.
        #modifyLabel(linesNumber, fontLinesNumber)
        # 1:清除磚塊.
        game_mode = 1

    # 初始方塊位置.
    container_x = 3
    container_y =-4

    # 現在出現方塊.
    brick_id = brick_next_id

    # 下個出現方塊.
    # 方塊編號(1~7).
    brick_next_id = random.randint( 1, 7)
    
    # 初始方塊狀態.
    brick_state = 0

    # GameOver.
    if (game_over):
        # 重新開始遊戲.
        resetGame()
    
#-------------------------------------------------------------------------
# 清除的方塊.
#-------------------------------------------------------------------------
def clearBrick():
    global bricks_array
    # 一列一列判斷清除方塊.
    temp = 0    
    for x in range(10):
        for i in range(19):
            for y in range(20):
                if (bricks_array[x][y] == 9):
                    if (y > 0):
                        temp = bricks_array[x][y - 1]
                        bricks_array[x][y - 1] = bricks_array[x][y]
                        bricks_array[x][y] = temp
                        y = y - 1
            bricks_array[x][0] = 0
#-------------------------------------------------------------------------
# 初始.
pygame.init()
# 顯示Title.
pygame.display.set_caption(u"俄羅斯方塊遊戲")
# 建立畫佈大小.
# 全螢幕模式.
canvas = pygame.display.set_mode((canvas_width, canvas_height), pygame.DOUBLEBUF and pygame.FULLSCREEN )
# 視窗模式.
#canvas = pygame.display.set_mode((canvas_width, canvas_height))

# 時脈.
clock = pygame.time.Clock()

# 查看系統支持那些字體
#print(pygame.font.get_fonts())

# 設定字型-黑體.
font = pygame.font.SysFont("simsunnsimsun", 24)


# 將繪圖方塊放入陣列.
for y in range(20):
    for x in range(10):
        bricks_list[x][y] = Box(pygame, canvas, "brick_x_" + str(x) + "_y_" + str(y), [ 0, 0, 26, 26], color_gray_block)

# 將繪圖方塊放入陣列.
for y in range(4):
    for x in range(4):
        bricks_next_object[x][y] = Box(pygame, canvas, "brick_next_x_" + str(x) + "_y_" + str(y), [ 0, 0, 26, 26], color_gray_block)

# 背景區塊.
background = Box(pygame, canvas, "background", [ 278, 18, 282, 562], color_gray)

# 背景區塊.
background_bricks_next = Box(pygame, canvas, "background_bricks_next", [ 590, 50, 114, 114], color_gray)

# 方塊編號(1~7).
brick_next_id = random.randint( 1, 7)
# 產生新磚塊.
brickNew()

#-------------------------------------------------------------------------    
# 主迴圈.
#-------------------------------------------------------------------------
running = True
time_temp = time.time()
time_now = 0
while running:
    # 計算時脈.
    time_now = time_now + (time.time() - time_temp)
    time_temp = time.time()
    #---------------------------------------------------------------------
    # 判斷輸入.
    #---------------------------------------------------------------------
    for event in pygame.event.get():
        # 離開遊戲.
        if event.type == pygame.QUIT:
            running = False        
        # 判斷按下按鈕
        if event.type == pygame.KEYDOWN:
            #-----------------------------------------------------------------
            # 判斷按下ESC按鈕
            if event.key == pygame.K_ESCAPE:
                running = False
            # 除錯訊息開關.
            elif event.key == pygame.K_d:
                debug_message = not debug_message                
            #-----------------------------------------------------------------
            # 變換方塊-上.
            elif event.key == pygame.K_UP and game_mode == 0:
                # 在右邊界不能旋轉.
                if (container_x == 8):
                    break
                # 判斷磚塊N1、N2、I.
                if (brick_id == 1 or brick_id == 2 or brick_id == 7):
                    # 長條方塊旋轉例外處理.
                    if (brick_id == 7):
                        if (container_x < 0 or container_x == 7):
                            break
                    # 旋轉方塊.
                    brick_state = brick_state + 1
                    if (brick_state > 1):
                        brick_state = 0                    
                    # 轉換定義方塊到方塊陣列.
                    transformToBricks(brick_id, brick_state)
                    # 碰到磚塊.
                    if (not ifCopyToBricksArray()):
                        brick_state = brick_state - 1
                        if (brick_state < 0):
                            brick_state = 1
                # 判斷磚跨L1、L2、T.                                
                elif (brick_id == 3 or brick_id == 4 or brick_id == 5):
                    # 旋轉方塊.
                    brick_state = brick_state + 1
                    if (brick_state > 3):
                        brick_state = 0                    
                    # 轉換定義方塊到方塊陣列.
                    transformToBricks(brick_id, brick_state)
                    # 碰到磚塊.
                    if (not ifCopyToBricksArray()):
                        brick_state = brick_state - 1
                        if (brick_state < 0):
                            brick_state = 3
            #-----------------------------------------------------------------
            # 快速下降-下.
            elif event.key == pygame.K_DOWN and game_mode == 0:
                # 磚塊快速下降.
                brick_down_speed = BRICK_DROP_RAPIDLY
            #-----------------------------------------------------------------
            # 移動方塊-左.
            elif event.key == pygame.K_LEFT and game_mode == 0:
                container_x = container_x - 1
                if (container_x < 0):
                    if (container_x == -1):
                        if (bricks[0][0] != 0 or bricks[0][1] != 0 or bricks[0][2] != 0 or bricks[0][3] != 0):
                            container_x = container_x + 1
                    elif (container_x == -2): 
                        if (bricks[1][0] != 0 or bricks[1][1] != 0 or bricks[1][2] != 0 or bricks[1][3] != 0):
                            container_x = container_x + 1
                    else:
                        container_x = container_x + 1
                # 碰到磚塊.
                if (not ifCopyToBricksArray()):
                    container_x = container_x + 1
            #-----------------------------------------------------------------
            # 移動方塊-右.
            elif event.key == pygame.K_RIGHT and game_mode == 0:
                container_x = container_x + 1
                if (container_x > 6):
                    if (container_x == 7):
                        if (bricks[3][0] != 0 or bricks[3][1] != 0 or bricks[3][2] != 0 or bricks[3][3] != 0):
                            container_x = container_x - 1;                        
                    elif (container_x == 8):
                        if (bricks[2][0] != 0 or bricks[2][1] != 0 or bricks[2][2] != 0 or bricks[2][3] != 0):
                            container_x = container_x - 1                        
                    else:
                        container_x = container_x - 1
                # 碰到磚塊.
                if (not ifCopyToBricksArray()):
                    container_x = container_x - 1                    
        #-----------------------------------------------------------------
        # 判斷放開按鈕
        if event.type == pygame.KEYUP:
            # 快速下降-下.
            if event.key == pygame.K_DOWN:
                # 恢復正常下降速度.
                brick_down_speed = BRICK_DOWN_SPEED_MAX
        
    #---------------------------------------------------------------------    
    # 清除畫面.
    canvas.fill(color_light_gray)

    # 遊戲中.
    if (game_mode == 0):
        # 處理磚塊下降.
        if(time_now >= brick_down_speed):
            # 往下降.
            container_y = container_y + 1; 
            # 碰到磚塊.
            if (not ifCopyToBricksArray()):
                #產生新塊.
                brickNew()            
            # 轉換定義方塊到方塊陣列(bricks).
            transformToBricks( brick_id, brick_state)
            # 清除時脈.
            time_now = 0
    # 清除磚塊.
    elif (game_mode == 1):
        # 清除的方塊.
        clearBrick()
        # 遊戲中.
        game_mode = 0
        # 轉換定義方塊到方塊陣列.
        transformToBricks(brick_id, brick_state)

    #---------------------------------------------------------------------    
    # 更新下一個磚塊圖形.
    updateNextBricks(brick_next_id)
    # 更新繪圖.
    pos_y = 20
    
    # ColorVer:設定背景顏色.
    background.color = color_block
    # 更新背景區塊.
    background.update()

    for y in range(20):
        pos_x = 280
        for x in range(10):
            if(bricks_array[x][y] != 0):
                bricks_list[x][y].rect[0] = pos_x
                bricks_list[x][y].rect[1] = pos_y

                # ColorVer:依照方塊編號設定顏色.
                if (bricks_array[x][y]==1):
                    bricks_list[x][y].color = box_color_orange
                elif (bricks_array[x][y]==2):
                    bricks_list[x][y].color = box_color_purple
                elif (bricks_array[x][y]==3):
                    bricks_list[x][y].color = box_color_blue
                elif (bricks_array[x][y]==4):
                    bricks_list[x][y].color = box_color_light_red
                elif (bricks_array[x][y]==5):
                    bricks_list[x][y].color = box_color_light_blue
                elif (bricks_array[x][y]==6):
                    bricks_list[x][y].color = box_color_yellow
                elif (bricks_array[x][y]==7):
                    bricks_list[x][y].color = box_color_green
                bricks_list[x][y].update()
            else:
                bricks_list[x][y].color = color_gray_block

            pos_x = pos_x + 28
        pos_y = pos_y + 28    
    
    # 更新掉落中方塊
    for y in range(4):
        for x in range(4):            
            if (bricks[x][y] != 0):
                posX = container_x + x
                posY = container_y + y
                if (posX >= 0 and posY >= 0):
                    bricks_list[posX][posY].rect[0] = (posX * 28) + 280
                    bricks_list[posX][posY].rect[1] = (posY * 28) + 20

                    # ColorVer:依照方塊編號設定顏色.
                    if (bricks[x][y]==1):
                        bricks_list[posX][posY].color = box_color_orange
                    elif (bricks[x][y]==2):
                        bricks_list[posX][posY].color = box_color_purple
                    elif (bricks[x][y]==3):
                        bricks_list[posX][posY].color = box_color_blue
                    elif (bricks[x][y]==4):
                        bricks_list[posX][posY].color = box_color_light_red
                    elif (bricks[x][y]==5):
                        bricks_list[posX][posY].color = box_color_light_blue
                    elif (bricks[x][y]==6):
                        bricks_list[posX][posY].color = box_color_yellow
                    elif (bricks[x][y]==7):
                        bricks_list[posX][posY].color = box_color_green
                    elif (bricks[x][y]==9):
                        bricks_list[posX][posY].color = color_white

                    bricks_list[posX][posY].update()
    
    #---------------------------------------------------------------------    
    # 除錯訊息.
    if(debug_message):
        # 更新容器.
        str_x = ""
        pos_x = 15
        pos_y = 20
        for y in range(20):
            str_x = ""
            for x in range(10):
                str_x = str_x + str(bricks_array[x][y]) + " "
            showFont( str_x, pos_x, pos_y, color_red)
            pos_y = pos_y + 28
            
        # 更新方塊
        posX = 0
        posY = 0    
        for y in range(4):
            str_x = ""
            for x in range(4):            
                if (bricks[x][y] != 0):
                    posX = container_x + x
                    posY = container_y + y
                    if (posX >= 0 and posY >= 0):
                        str_x = str_x + str(bricks[x][y]) + " "
                else:
                    str_x = str_x + "  "
            pos_x = 15 + (container_x * 26)
            pos_y = 20 + (posY * 28)
            showFont( str_x, pos_x, pos_y, color_white)

    # ColorVer:顯示訊息.
    showFont( u"下次出現方塊", 588, 16, color_block)

    showFont( u"最大連線數", 588, 190, color_block)
    showFont( str(int(lines_number_max)), 588, 220, color_block)

    showFont( u"本局連線數", 588, 260, color_block)
    showFont( str(int(lines_number)), 588, 290, color_block)

    # 顯示FPS.
    # 除錯訊息.
    if(debug_message):    
        showFont( u"FPS:" + str(clock.get_fps()), 6, 0, color_gray_green)    

    # 更新畫面.
    pygame.display.update()
    clock.tick(60)

# 離開遊戲.
pygame.quit()
quit()