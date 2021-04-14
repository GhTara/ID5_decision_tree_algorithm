from anytree import NodeMixin, RenderTree
from instance import Instance
from math import log2


class Tree(NodeMixin):
    def __init__(self, attribute_name, classes_num, childs_value, is_attr, parent=None):
        self.attribute_name = attribute_name
        self.classes_num = classes_num
        self.parent = parent
        self.childs_value = childs_value
        self.childs_dict = {}
        self.is_attr = is_attr
        self.num_false = 0

        if is_attr:
            for attri_val in childs_value:
                self.childs_dict[attri_val] = None
        self.instances = []

    def add_instance_propagte(self, instance):

        self.instances.append(instance)
        self.update_class_num(instance)
        self = self.parent
        if not self:
            return
        self.add_instance_propagte(instance)

    def update_class_num(self, instance):
        # [#positive, #negative]
        self.classes_num[0] += (instance.class_value)
        self.classes_num[1] += (1 - instance.class_value)

    def add_instance(self, instance, attribute_value_dict):

        # change = False
        # attribute_name = instance.attribues_value[self.attribute_name]
        # if not self.childs_dict[attribute_name]:
        #     node = Tree(attribute_name=None, classes_num=[
        #                 0, 0], childs_value=None, parent=self, is_feature=False)
        #     self.childs_dict[attribute_name] = node
        # node = self.childs_dict[attribute_name]
        # self.childs_dict[attribute_name].add_instance_propagte(instance)
        # if 0 not in node.classes_num:
        #     change = True

        # ---------------------------------------------------------------------------
        blocked_list = []
        change = False
        node = self
        parent_temp = None
        # iterative
        while node.is_attr:
            blocked_list.append(node.attribute_name)
            node.instances.append(instance)
            node.update_class_num(instance)
            attribute_name = instance.attribues_value[node.attribute_name]
            parent_temp = node

            node = node.childs_dict[attribute_name]

            if not node:
                break
            if not node.is_attr:
                break

        if parent_temp and not node:
            node = Tree(attribute_name=None, classes_num=[
                        0, 0], childs_value=None, parent=parent_temp, is_attr=False)
            parent_temp.childs_dict[attribute_name] = node

        node = parent_temp.childs_dict[attribute_name]
        node.instances.append(instance)
        node.update_class_num(instance)

        if 0 not in node.classes_num:

            instances = node.instances
            if len(blocked_list) < len(attribute_value_dict.keys()):
                best_attr = find_best_attr(
                    instances, blocked_list, attribute_value_dict)
                node.attribute_name = best_attr
                # print(
                #     best_attr, attribute_value_dict[best_attr], '---------------')
                # add children attributes to node
                for attri_val in attribute_value_dict[best_attr]:
                    node.childs_dict[attri_val] = None
                node.is_attr = True
                insts = node.instances
                for ins in insts:
                    node.add_instance_leaf(ins)
                # add instances to this node
                change = True

        return change, node

    def add_instance_leaf(self, instance):
        if self.is_attr:
            attribut_value = instance.attribues_value[self.attribute_name]
            node = self.childs_dict[attribut_value]
            if not node:
                node = Tree(attribute_name=None, classes_num=[
                    0, 0], childs_value=None, parent=self, is_attr=False)
                self.childs_dict[attribut_value] = node

            node.instances.append(instance)
            node.update_class_num(instance)

    def dfs(self, attribute_value_dict):

        if self.attribute_name:
            for attr_val in self.childs_dict.keys():
                if self.childs_dict[attr_val]:
                    if self.childs_dict[attr_val].attribute_name:
                        self.childs_dict[attr_val].dfs(attribute_value_dict)
                        self.childs_dict[attr_val].check_pull_up(
                            attribute_value_dict)
            if not self.parent:
                self.check_pull_up(attribute_value_dict)

    def check_pull_up(self, attribute_value_dict):
        # print(self.attribute_name, end=' ')

        i = 0
        for attr_val, child in self.childs_dict.items():
            i += 1
            # print(i, '------------------------')

            if i > 100:
                None
                # print(i)
                # break
            if child:
                if child.is_attr:
                    if attr_entropy(child.attribute_name, child.instances, attribute_value_dict) < attr_entropy(self.attribute_name, self.instances, attribute_value_dict):
                        # set the child as root of the tree
                        new_tree_root = Tree(child.attribute_name, [
                            0, 0], attribute_value_dict[child.attribute_name], True, None)
                        # add old parent to each of value of new root attributes
                        for attr_val_child in new_tree_root.childs_value:
                            node_temp = Tree(attr_val_child, [
                                0, 0], self.childs_value, False, new_tree_root)
                            new_tree_root.childs_dict[attr_val_child] = node_temp
                        instances = self.instances
                        self = new_tree_root

                        # recreat tree
                        for instance in instances:
                            is_change, leaf_node = self.add_instance(
                                instance, attribute_value_dict)

    def output_test(self, instance, attribute_value_dict):
        node = self
        # print('__________________________')
        # print(instance.attribues_value)
        while node.attribute_name:
            l = 0
            if node.classes_num[0] >= node.classes_num[1]:
                l = 1
            else:
                l = 0
            if l != instance.class_value:
                node.num_false += 1
            # print(node.attribute_name)
            attr_value = instance.attribues_value[node.attribute_name]
            parent = node
            # print(node.childs_dict)
            node = node.childs_dict[attr_value]

            if not node:
                # node = parent
                # the data can't reach to leaf
                # break
                return -1
            if not node.attribute_name:
                break

        if node.classes_num[0] >= node.classes_num[1]:
            return 1
        else:
            return 0

    def reduced_error_pruning(self, attribute_value_dict):
        if self.attribute_name:
            prun = False
            for attr_val in self.childs_dict.keys():
                if self.childs_dict[attr_val]:
                    # to do
                    if prun:
                        self.childs_dict[attr_val] = None
                        print(self.childs_dict[attr_val].attribute_name)
                    if self.childs_dict[attr_val].num_false > self.childs_dict[attr_val].parent.num_false:
                        prun = True
                        self.childs_dict[attr_val] = None
                        print(self.childs_dict[attr_val].attribute_name)

    # Prints the n-ary tree level wise
    '''
    def reduced_error_pruning(self):

        if (self == None):
            return

        # standard level order traversal code (bfs)
        # using queue
        q = []  # Create a queue
        q.append(self)  # Enqueue root
        while (len(q) != 0):

            n = len(q)

            # If this node has children
            while (n > 0):

                # Dequeue an item from queue and print it
                p = q[0]
                q.pop(0)

                # print(p.attribute_name, end=' ')

                # Enqueue all children of the dequeued item
                for attr in p.childs_dict.keys():
                    if p.childs_dict[attr]:
                        # print(p.childs_dict[attr].num_false)
                        if p.childs_dict[attr].num_false > p.num_false:
                            p.childs_dict[attr] = None
                        else:
                            q.append(p.childs_dict[attr])
                n -= 1

            # print()
'''
    '''def reduced_error_pruning(self):
        if not self:
            return
        if not self.is_attr:
            return
        for attr_val in self.childs_dict.keys():
            if self.childs_dict[attr_val]:
                if self.num_false < self.childs_dict[attr_val].num_false:
                    self.childs_dict[attr_val] = None
                else:
                    self = self.childs_dict[attr_val]
                    self.reduced_error_pruning()
'''


def attr_entropy(attribute, instances, attribute_value_dict):
    attr_antropy_dict = {}
    # initialization
    for attr_val in attribute_value_dict[attribute]:
        attr_antropy_dict[attr_val] = []
     # devot every instance to each attr_value
    for instance in instances:
        attr_antropy_dict[instance.attribues_value[attribute]].append(
            instance)
    # calculate weighted average of antorpies
    total_size = len(instances)
    ave = 0
    for key, list_instance in attr_antropy_dict.items():
        ave += entropy(list_instance)*(len(list_instance)/total_size)

    return ave


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


def find_best_attr(instances, blocked_attrs, attribute_value_dict):
    dict_attr_entropy = {attribute: attr_entropy(attribute, instances, attribute_value_dict)
                         for attribute in attribute_value_dict.keys() if attribute not in blocked_attrs}
    # lowest E-score => best attribute
    best_attr = min(dict_attr_entropy, key=(
        lambda k: dict_attr_entropy[k]))

    return best_attr
