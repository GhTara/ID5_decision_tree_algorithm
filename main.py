import xlrd
from instance import Instance
import pandas as pd
from tree import Tree
from math import log2
from anytree import NodeMixin, RenderTree


def load_data(filename):
    global attribute_value_dict
    attribute_value_dict = {}
    print('[1] Loading Data ....')
    data = pd.read_excel(filename)
    instances = []
    attrs = list(data.columns)
    for i, row in data.iterrows():
        values = [item for i, item in row.iteritems()]
        attrs_val = dict(zip(attrs[0:-2], values[0:-2]))
        class_val = 0 if values[-1] == 'no' else 1
        instance = Instance(attrs_val, class_val)
        instances.append(instance)

    for key in instances[0].attribues_value.keys():
        attribute_value_dict[key] = list(
            set([instance.attribues_value[key] for instance in instances]))
    return instances


def kfoldCrossValid(k, data, purning=False):
    global attribute_value_dict
    global tree_root
    sizeFold = len(data)//k
    total_precision = 0

    # '''

    # for i in range(1):
    for i in range(k):

        if (i+1)*sizeFold < len(data):
            hold_out = data[i*sizeFold:(i+1)*sizeFold]
        else:
            hold_out = data[i*sizeFold:]

        train_data = list(set(data) - set(hold_out))
        # make tree on current train data
        makeTree(train_data)

        # check entropy(child) < entropy(parent) for pull-up
        tree_root.dfs(attribute_value_dict)
        print(tree_root.attribute_name)
        print_tree(tree_root)
        # precision = test on current tree for curren hold out data
        precision = calculate_precision(hold_out)
        if purning:
            tree_root.reduced_error_pruning(attribute_value_dict)
        for pre, fill, node in RenderTree(tree_root):
            treestr = u"%s%s" % (pre, node.attribute_name)
            if node.attribute_name:
                print(treestr.ljust(8), node.classes_num)

        total_precision += precision

    return total_precision / k
    # '''


def all(data):

    # make tree on current train data
    makeTree(data)
    # check entropy(child) < entropy(parent) for pull-up
    tree_root.dfs(attribute_value_dict)
    # precision = test on current tree for curren hold out data
    precision = calculate_precision(data)
    if purning:
        tree_root.reduced_error_pruning(attribute_value_dict)

    return precision


def makeTree(train_data):
    global current_instances
    global tree_root
    global attribute_value_dict
    current_instances = []

    # calculate global entropy each iteration
    while entropy(current_instances) == 0:
        current_instances.append(train_data.pop(0))
    choose_root()

    for instance in train_data:
        current_instances.append(instance)
        tree_root.add_instance(
            instance, attribute_value_dict)


def entropy(instances):
    if len(instances) == 0:
        return 0
    pos_num = 0
    neg_num = 0
    for instance in instances:
        if instance.class_value == 1:
            pos_num += 1
        elif instance.class_value == 0:
            neg_num += 1
    pos_p = pos_num / (pos_num + neg_num)
    neg_p = 1 - pos_p
    if pos_num == 0 or neg_num == 0:
        return 0
    return -(pos_p*log2(pos_p)+neg_p*log2(neg_p))


def choose_root():
    global blocked_attrs
    global tree_root
    global current_instances
    global attribute_value_dict
    blocked_attrs = []
    # calculate E_score for each attribute
    best_attr = find_best_attr(instances)

    # choose a root for tree
    tree_root = Tree(attribute_name=best_attr,
                     classes_num=[0, 0], childs_value=attribute_value_dict[best_attr], is_attr=True)
    # add to blocked list
    blocked_attrs.append(best_attr)

    # make empty current data to add them to tree in next step
    for instance in current_instances:
        is_change, node = tree_root.add_instance(
            instance, attribute_value_dict)
    current_instances = []


def find_best_attr(instances):
    global attribute_value_dict
    global blocked_attrs
    dict_attr_entropy = {attribute: attr_entropy(attribute, instances)
                         for attribute in attribute_value_dict.keys() if attribute not in blocked_attrs}
    # lowest E-score => best attribute
    best_attr = min(dict_attr_entropy, key=(lambda k: dict_attr_entropy[k]))

    return best_attr


def attr_entropy(attribute, instances):
    global attribute_value_dict
    attr_antropy_dict = {}
    # initialization
    for attr_val in attribute_value_dict[attribute]:
        attr_antropy_dict[attr_val] = []
    # devote every instance to each attr_value
    for instance in instances:
        attr_antropy_dict[instance.attribues_value[attribute]].append(instance)
    # calculate weighted average of antorpies
    total_size = len(instances)
    ave = 0
    for key, list_instance in attr_antropy_dict.items():
        ave += entropy(list_instance)*(len(list_instance)/total_size)

    return ave




def calculate_precision(test_data):
    global tree_root
    global attribute_value_dict
    correct = 0
    minus = 0
    total = len(test_data)
    for ins in test_data:
        out = tree_root.output_test(ins, attribute_value_dict)
        if out == -1:
            minus -= 1
        elif out == ins.class_value:
            correct += 1
    return float(correct) / float(total+minus)


file_name = 'data.xls'
instances = load_data(file_name)
# print(instances[3].attribues_value, instances[3].class_value)
error = kfoldCrossValid(k=5, data=instances, purning=True)
print(error)
# error2 = all(instances)
# print(error2)
