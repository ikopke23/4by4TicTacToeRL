import numpy as np
import pickle
import os
import shutil
import sys
import time

BOARD_ROWS = 4
BOARD_COLS = 4


class State:
    def __init__(self, p1, p2):
        self.board = np.zeros((BOARD_ROWS, BOARD_COLS))
        self.p1 = p1
        self.p2 = p2
        self.isEnd = False
        self.boardHash = None
        # init p1 plays first
        self.playerSymbol = 1

    # get unique hash of current board state
    def getHash(self):
        self.boardHash = str(self.board.reshape(BOARD_COLS * BOARD_ROWS))
        return self.boardHash

    def winner(self):
        # row
        for i in range(BOARD_ROWS):
            if sum(self.board[i, :]) == 4:
                self.isEnd = True
                return 1
            if sum(self.board[i, :]) == -4:
                self.isEnd = True
                return -1
        # col
        for i in range(BOARD_COLS):
            if sum(self.board[:, i]) == 4:
                self.isEnd = True
                return 1
            if sum(self.board[:, i]) == -4:
                self.isEnd = True
                return -1
        # diagonal
        diag_sum1 = sum([self.board[i, i] for i in range(BOARD_COLS)])
        diag_sum2 = sum([self.board[i, BOARD_COLS - i - 1] for i in range(BOARD_COLS)])
        diag_sum = max(abs(diag_sum1), abs(diag_sum2))
        if diag_sum == 4:
            self.isEnd = True
            if diag_sum1 == 4 or diag_sum2 == 4:
                return 1
            else:
                return -1

        # tie
        # no available positions
        if len(self.availablePositions()) == 0:
            self.isEnd = True
            return 0
        # not end
        self.isEnd = False
        return None

    def availablePositions(self):
        positions = []
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if self.board[i, j] == 0:
                    positions.append((i, j))  # need to be tuple
        return positions

    def updateState(self, position):
        self.board[position] = self.playerSymbol
        # switch to another player
        self.playerSymbol = -1 if self.playerSymbol == 1 else 1

    # only when game ends
    def giveReward(self):
        result = self.winner()
        # backpropagate reward
        if result == 1:
            self.p1.feedReward(1)
            self.p2.feedReward(-0.5)
        elif result == -1:
            self.p1.feedReward(-0.5)
            self.p2.feedReward(1)
        else:
            self.p1.feedReward(0.1)
            self.p2.feedReward(0.5)

    # board reset
    def reset(self):
        self.board = np.zeros((BOARD_ROWS, BOARD_COLS))
        self.boardHash = None
        self.isEnd = False
        self.playerSymbol = 1

    def play(self, rounds=100):
        modA = 5000
        # print("rounds = " + str(rounds)+"\n")
        # print("modA = " + str(modA)+"\n")

        for i in range(rounds):
            # self.showBoard();
            if i% modA == 0:
                f = open("games/gamefile"+str(i)+".txt", "x")

            if i != 1 and i% modA == 0:
                f.write("isEnd = "+ str(self.isEnd)+"\n")
            # else:
                # print("isEnd = "+ str(self.isEnd)+"\n")
            # if i % 1000 == 0:

                # print("Rounds {}".format(i))
            while not self.isEnd:
                # Player 1
                positions = self.availablePositions()
                p1_action = self.p1.chooseAction(positions, self.board, self.playerSymbol, f, modA, rounds)
                # take action and upate board state
                self.updateState(p1_action)
                board_hash = self.getHash()
                self.p1.addState(board_hash)
                # check board status if it is end
                self.showBoard(f, modA, i)
                win = self.winner()
                if win is not None:
                    if rounds % 100 == 0:
                        self.showBoard(f, modA, i)
                    # ended with p1 either win or draw
                    self.giveReward()
                    self.p1.reset()
                    self.p2.reset()
                    self.reset()
                    break

                else:
                    # Player 2
                    positions = self.availablePositions()
                    p2_action = self.p2.chooseAction(positions, self.board, self.playerSymbol, f, modA, i)
                    self.updateState(p2_action)
                    board_hash = self.getHash()
                    self.p2.addState(board_hash)

                    win = self.winner()
                    if win is not None:
                        # self.showBoard()
                        # ended with p2 either win or draw
                        self.giveReward()
                        self.p1.reset()
                        self.p2.reset()
                        self.reset()
                        break

    # play with human
    def play2(self):
        while not self.isEnd:
            # Player 1
            positions = self.availablePositions()
            f = 0
            modA = 1
            rounds = 1
            p1_action = self.p1.chooseAction(positions, self.board, self.playerSymbol, f, modA, rounds)
            # take action and upate board state
            self.updateState(p1_action)
            self.showBoard(f, rounds)
            # check board status if it is end
            win = self.winner()
            if win is not None:
                if win == 1:
                    print(self.p1.name, "wins!\n")
                else:
                    print("tie!\n")
                self.reset()
                break

            else:
                # Player 2
                positions = self.availablePositions()
                p2_action = self.p2.chooseAction(positions, f, modA, rounds)

                self.updateState(p2_action)
                self.showBoard(f, rounds)
                win = self.winner()
                if win is not None:
                    if win == -1:
                        print(self.p2.name, "wins!\n")
                    else:
                        print("tie!\n")
                    self.reset()
                    break


    def play3(self, rounds=100):
        print("rounds = " + str(rounds)+"\n")
        
        for i in range(rounds):
            modA = 0
            self.showBoard2()
            while not self.isEnd:
                # Player 1
                positions = self.availablePositions()
                p1_action = self.p1.chooseAction2(positions, self.board, self.playerSymbol)
                # take action and upate board state
                self.updateState(p1_action)
                board_hash = self.getHash()
                self.p1.addState(board_hash)
                # check board status if it is end
                self.showBoard2()
                win = self.winner()
                if win is not None:
                    if rounds % 100 == 0:
                        self.showBoard2()
                    # ended with p1 either win or draw
                    self.giveReward()
                    self.p1.reset()
                    self.p2.reset()
                    self.reset()
                    break

                else:
                    # Player 2
                    positions = self.availablePositions()
                    p2_action = self.p2.chooseAction2(positions, self.board, self.playerSymbol)
                    self.updateState(p2_action)
                    board_hash = self.getHash()
                    self.p2.addState(board_hash)

                    win = self.winner()
                    if win is not None:
                        # self.showBoard()
                        # ended with p2 either win or draw
                        self.giveReward()
                        self.p1.reset()
                        self.p2.reset()
                        self.reset()
                        break


    def showBoard(self,f,rounds, modA = 50):
        # p1: x  p2: o
        if modA != 1 and f != 0:
            f.write(str(self.board))
            for i in range(0, BOARD_ROWS):
                f.write('\n-----------------\n')
                out = '\n|'
                for j in range(0, BOARD_COLS):
                    if self.board[i, j] == 1:
                        token = 'x'
                    if self.board[i, j] == -1:
                        token = 'o'
                    if self.board[i, j] == 0:
                        token = ' '
                    if j == 3 and i == 3:
                        out += token + ' | \n'
                    else :
                        out += token + ' | '
                f.write(out)
            f.write('-----------------\n')
        else:
            print(self.board)
            for i in range(0, BOARD_ROWS):
                print('-----------------')
                out = '| '
                for j in range(0, BOARD_COLS):
                    if self.board[i, j] == 1:
                        token = 'x'
                    if self.board[i, j] == -1:
                        token = 'o'
                    if self.board[i, j] == 0:
                        token = ' '
                    out += token + ' |'
                print(out)
            print('-----------------')
    def showBoard2(self):
            print(self.board)
            for i in range(0, BOARD_ROWS):
                print('-----------------')
                out = '| '
                for j in range(0, BOARD_COLS):
                    if self.board[i, j] == 1:
                        token = 'x'
                    if self.board[i, j] == -1:
                        token = 'o'
                    if self.board[i, j] == 0:
                        token = ' '
                    out += token + ' |'
                print(out)
            print('-----------------')


class Player:
    def __init__(self, name, exp_rate=0.3):
        self.name = name
        self.states = []  # record all positions taken
        self.lr = 0.2
        self.exp_rate = exp_rate
        self.decay_gamma = 0.94
        self.states_value = {}  # state -> value

    def getHash(self, board):
        boardHash = str(board.reshape(BOARD_COLS * BOARD_ROWS))
        return boardHash

    def chooseAction(self, positions, current_board, symbol, f, modA, rounds):
        if np.random.uniform(0, 1) <= self.exp_rate:
            # take random action
            # print("RANDOM ACTION")
            idx = np.random.choice(len(positions))
            action = positions[idx]
            if rounds != 1 and rounds% modA == 0:

                f.write("RANDOMLY CHOSEN" + str(action)+"\n")
            # else:
                # print(str(action)+"\n")


        else:
            value_max = -9999
            for p in positions:
                # print("p = " + str(p))
                # print("positions = " + str(positions))
                next_board = current_board.copy()
                next_board[p] = symbol
                # print("next_board " + str(next_board))
                next_boardHash = self.getHash(next_board)
                value = 0 if self.states_value.get(next_boardHash) is None else self.states_value.get(next_boardHash)
                if rounds != 1 and rounds% modA == 0:
                    f.write("position p = "+str(p)+ " with a value of " +  str(value)+"\n")
                    # f.write("value_max" +str(value_max))
                # else:
                    # print("value_max" +str(value_max))
                    # print("value", value)
                if value >= value_max:
                    value_max = value
                    action = p
        # print("{} takes action {}".format(self.name, action))
        return action

    def chooseAction2(self, positions, current_board, symbol):
        if np.random.uniform(0, 1) <= self.exp_rate:
            # take random action
            print("RANDOM ACTION")
            idx = np.random.choice(len(positions))
            action = positions[idx]
            # if rounds != 1 and rounds% modA == 0:

                # f.write("RANDOMLY CHOSEN" + str(action)+"\n")
            # else:
            print(str(action)+"\n")


        else:
            value_max = -9999
            for p in positions:
                next_board = current_board.copy()
                next_board[p] = symbol
                # print("next_board " + str(next_board))
                next_boardHash = self.getHash(next_board)
                value = 0 if self.states_value.get(next_boardHash) is None else self.states_value.get(next_boardHash)
            
                # print("value_max" +str(value_max))
                # print("value", value)
                if value >= value_max:
                    value_max = value
                    action = p
        # print("{} takes action {}".format(self.name, action))
        return action


    # append a hash state
    def addState(self, state):
        self.states.append(state)

    # at the end of game, backpropagate and update states value
    def feedReward(self, reward):
        for st in reversed(self.states):
            if self.states_value.get(st) is None:
                self.states_value[st] = 0
            self.states_value[st] += self.lr * (self.decay_gamma * reward - self.states_value[st])
            reward = self.states_value[st]

    def reset(self):
        self.states = []

    def savePolicy(self):
        fw = open('policy_' + str(self.name), 'wb')
        pickle.dump(self.states_value, fw)
        fw.close()

    def loadPolicy(self, file):
        fr = open(file, 'rb')
        self.states_value = pickle.load(fr)
        fr.close()


class HumanPlayer:
    def __init__(self, name):
        self.name = name

    def chooseAction(self, positions, f, modA, rounds):
        while True:
            row = int(input("Input your action row:"))
            col = int(input("Input your action col:"))
            action = (row, col)
            if action in positions:
                return action

    # append a hash state
    def addState(self, state):
        pass

    # at the end of game, backpropagate and update states value
    def feedReward(self, reward):
        pass

    def reset(self):
        pass



def play(argv):
    if argv[2] == "human":
        p2 = Player("computer", 0)
        p2.loadPolicy("policy_p2")

        p1 = HumanPlayer("human")
        st = State(p1,p2)
        st.play2()
    else:
        p1 = Player("computer", 0)
        p1.loadPolicy("policy_p1")

        p2 = HumanPlayer("human")
        st = State(p1,p2)
        st.play2()
#END play

def training(argv):
    # deleting and making a new folder to house the games
    # parent_dir = "/Users/iankopke/Code/RLstuff/TicTacToe" # For desktop
    # parent_dir = "/Users/IanK/Downloads/RLstuff/TicTacToe" # for laptop
    parent_dir = "/home/iankopke/GitHub/4by4TicTacToeRL" # for Linux laptop
    directory = "games"
    # shutil.rmtree("/Users/IanK/Downloads/RLstuff/TicTacToe/games") # for Desktop
    # shutil.rmtree("/Users/IanK/Downloads/RLstuff/TicTacToe/games") # for laptop
    shutil.rmtree("/home/iankopke/GitHub/4by4TicTacToeRL/games")
    path = os.path.join(parent_dir, directory)
    mode = 0o777
    path = os.path.join(parent_dir, directory)
    os.mkdir(path, mode)
    # training
    p1 = Player("p1", exp_rate = float(argv[3]))
    p2 = Player("p2", exp_rate = 0.6)

    st = State(p1, p2)
    print("training...")
    st.play(int(argv[2]))
    p1.savePolicy()
    finalTime = time.time()
    totalTime = (finalTime-initTime)
    print("It took " + str((totalTime)/60) +" minutes to run " + argv[2] + " games")
    print("Thats an avg of " + str((totalTime/int(argv[2]))) +" seconds a game")
#END training

def save(argv):
    # parent_dir = "/Users/iankopke/Code/RLstuff/TicTacToe" # For desktop
    # parent_dir = "/Users/IanK/Downloads/RLstuff/TicTacToe/savedGames" # for laptop
    parent_dir = "/home/iankopke/GitHub/4by4TicTacToeRL/savedGames"
    directory = argv[2]
    # gameFolder = "/Users/IanK/Downloads/RLstuff/TicTacToe/games" # for Desktop
    # gameFolder = "/Users/IanK/Downloads/RLstuff/TicTacToe/games" # for laptop
    gameFolder = "/home/iankopke/GitHub/4by4TicTacToeRL/games" # for linux
    # shutil.rmtree("/Users/IanK/Downloads/RLstuff/TicTacToe/games") # for Desktop
    # shutil.rmtree("/Users/IanK/Downloads/RLstuff/TicTacToe/games") # for laptop
    path = os.path.join(parent_dir, directory)
    mode = 0o777
    path = os.path.join(parent_dir, directory)
    os.mkdir(path, mode)
    for i in range(0, int(argv[3]), 5000):
        src = gameFolder+"/gamefile"+str(i)+".txt"
        shutil.copy2(src, path)
# END save

def backup(argv):
    parent_dir = "/home/iankopke/GitHub/4by4TicTacToeRL/savedPolicies" # for laptop
    directory = argv[3]+".txt"
    path = os.path.join(parent_dir, directory)
    mode = 0o777
    path = os.path.join(parent_dir, directory)
    if (argv[2] == 1):
        src = parent_dir+"policy_p1"
    else:
        src = parent_dir+"policy_p2" #END IF
    shutil.copy(src, path)

#END Backup

def testpol(argv):
    # dire = "/home/iankopke/GitHub/4by4TicTacToeRL/savedPolicies/"
    currentDire = "/home/iankopke/GitHub/4by4TicTacToeRL/"
    p1File =  currentDire+argv[2]
    p2File = currentDire+argv[3]
    # shutil.move(dire+argv[2], p1File)
    # shutil.move(dire+argv[3], p1File)
    
    p1 = Player("Computer", 0)
    p1.loadPolicy(p1File)
    p2 = Player("Computer", 0)
    p1.loadPolicy(p2File)
    st = State(p1, p2)
    st.play3(1)
    # shutil.move(p1File, dire+argv[2])
    # shutil.move(p2File, dire+argv[3]) 
    



if __name__ == "__main__":
    initTime = time.time()
    # testingtestpol = [0,"test", "500k44exp88yP1", "500k44exp88yP1"]
    # testpol(testingtestpol)
    if len(sys.argv) == 1:
        print("Please input whether you would like to play, train, save, backup (Policy), or test policies")
        args = [sys.argv, "", "", "", ""]
        args[1] = input()

        if args[1] == "play":
            print("Please indicate who you would like to go first (Human or Computer)")
            print("Please note that the Human playing first is not functional")
            args[2] = input()
            play(args);
        elif args[1] == "train":
            print("Please input how many games it should run")
            args[2] = input()
            print("Please input the experiment rate in range 0-1. The default is 0.3")
            args[3] = input()
            training(args)
        elif args[1] == "save":
            print("Please input directory name")
            args[2] = input()
            print("Please input how many games are being saved")
            args[3] = input()
            save(args);
        elif args[1] == "backup":
            print("Please indicate which policy you want to save 1 or 2")
            args[2] == input()
            print("Please input the name of the new saved file")
            args[3] == input()
            backup(args)
        # elif args[1] == "test":
        #     print("Please indicate the name of p1")
        #     print("Please note that it must be a saved policy")
        #     args[2] == input()
        #     print("Please indicate the name of p2")
        #     print("Please note that it must be a saved policy")
        #     args[3] == input()
        #     testpol(args)
    elif sys.argv[1] == "train":
        training(sys.argv)
    elif sys.argv[1] == "play":
        play(sys.argv)
    elif sys.argv[1] == "save":
        save(sys.argv)
    elif sys.argv[1] == "backup":
        backup(sys.argv)
    elif sys.argv[1] == "test":
        testpol(sys.argv)
# END MAIN
