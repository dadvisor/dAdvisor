from . import waste_collector

if __name__ == '__main__':
    import random
    num_tests = 1000
    max_elements = 20

    waste = waste_collector.WasteCollector()

    for j in range(num_tests):
        print('Test ' + str(j))
        elements = random.randint(0, max_elements)
        util_list = []
        for i in range(elements):
            item = random.random()
            while item == 0:
                item = random.random()
            util_list.append(item / max_elements)
        waste_list = waste.get_waste(util_list)
        waste_list2 = waste.get_waste_fast(util_list)
        if waste_list != waste_list2:
            print('Error: list not the same')
            print(util_list)
            print(waste_list)
            print(waste_list2)
            break
