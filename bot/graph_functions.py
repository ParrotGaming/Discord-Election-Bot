def createCandidateGraph():
    import os

    if os.path.exists("output.png"):
        os.remove("output.png")
        print("image removed")
    else:
        print("404")

    import matplotlib.pyplot as plt
    from db_interact import getGraphData

    data = getGraphData()
    labels = []

    for name in data:
        if name[3] != 0:
            labels.append(name[1])

    sizes = []

    for vote in data:
        if vote[3] != 0:
            sizes.append(vote[3])

    plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=False, startangle=140)

    plt.axis('equal')
    plt.savefig('output')
    plt.figure().clear()