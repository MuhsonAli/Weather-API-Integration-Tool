def longest_consecutive_sequence(*numbers):
    new = []
    for i in numbers:
        new.append(i)
        new.sort()

    for i in range(len(new)):
        result = []
        temp = new[i]
        i += 1
        if new[i] - temp == 1:
            result.append(temp)
            print(result)




longest_consecutive_sequence(100, 4, 200, 1, 3, 2)