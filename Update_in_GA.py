def fitness(grid):
    ErrorCount = 0
    total = 0
    for i in range(0,9):
        ErrorCount = (9 - len(np.unique(grid[:,i]))) + (9 - len(np.unique(grid[i,:])))
        total = total + ErrorCount
    for i in range(0,3):
        for j in range(0,3):
            ErrorCount = 9 - len(np.unique(grid[i*3:(i*3)+3,j*3:(j*3)+3]))
            total = total + ErrorCount
    return total

def mutate(gridtemp , flag):
    temporary = gridtemp.copy()
    while True:
        row1 =  random.randint(0,8)
        col1 =  random.randint(0,8)
        if flag[row1][col1] != 1:
            if random.random() < 1:
                temporary[row1][col1] = random.randint(1,9)
            break
    return temporary

