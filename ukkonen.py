class End:
    """
    End pointer class to keep track of the current end of the string. Will
    be incremented when the i pointer is incremented.
    """
    def __init__(self) -> None:
        """
        Pointer to the end of the string. Starts with -1 because the string is 0 indexed
        """
        # the global end pointer
        self.end_pointer = -1

    def extend(self) -> None:

        """
        Increments the end pointer by 1.
        """
        self.end_pointer += 1

class Node:
    def __init__(self, start: int, end, incoming = None, suffix_link = None, leaf_node = False) -> None:
        """
        Node class for the Ukkonen's algorithm. Each node will have a start and end pointer.
        """

        # parent node
        self.incoming = incoming

        # the starting index of the substring of the text
        self.start = start

        # the ending index of the substring of the text
        # if the node is a leaf node, the end pointer will be the end pointer of the End class
        # if not, then it will be an integer
        self.end = end

        # suffix link of the node
        self.suffix_link = suffix_link 

        # list of suffix id
        # to keep track which suffixes are connected to the node
        self.connected_to = []
        
        # to save the j pointer in the leaf node
        self.j = None

        # boolean to check if the node is a leaf node
        self.leaf_node = leaf_node
        
        # from the assumption that all input strings come from the restricted ASCII range [37, 126]
        # 91 is the number of characters in the range plus the '$' character which will be in index 0
        self.child_nodes = [None] * 91

    def __getitem__(self, __index: int):
        """
        Returns the child node at the given index
        """
        return self.child_nodes[__index]
    
    def __setitem__(self, __index: int, value):
        """
        Sets the child node at the given index
        """
        self.child_nodes[__index] = value

    def get_end(self) -> int:
        """
        Returns the end of the node
        """
        try:
            # try to get the end pointer from the End class
            return self.end.end_pointer
        except:
            # if the end is not the End class, then it is an integer
            return self.end

    def get_length(self) -> int:
        """
        Returns the length of the node. This is
        done by getting the difference between the end and start pointer
        """
        return self.get_end() - self.start
        
    def is_leaf(self) -> bool:
        """
        Returns True if the node is a leaf node.
        False otherwise.
        """
        return self.leaf_node
    
    def get_start(self) -> int:
        """
        Returns the start of the node. Or where the node starts in the string.
        """
        return self.start
    
class Ukkonen:

    def __init__(self, text: str, end: End = End()) -> None:
        """
        Ukkonen's algorithm class. This class will be used to create the suffix tree. Also,
        will contain the method for the in order traversal.
        """

        # the root node of the suffix tree
        self.root = Node(0, end)

        # the suffix link of the root node will be itself
        self.root.suffix_link = self.root

        # the active node of the algorithm. Starts with the root node
        self.active_node = self.root

        # to keep track of the previous internal node
        self.previous_node = None

        # the end pointer of the string
        self.end = end
        
        # the length of the active edge
        self.active_length = 0

        # to build the suffix tree
        self.run_algorithm(text)

    def run_algorithm(self, text):
        """
        Runs the Ukkonen's algorithm to build the suffix tree. It uses tricks from the tutorial videos
        but the implementation of the proper suffix link is not implemented. In this code, all suffix links points
        to the root node.

        Input:
        :text           : a string

        Time complexity: 
            :Worst          : O(N), where n is the length of the string
        Space complexity:
            :Aux            : O(N)

        Citation: FIT 3155 Workshop live coding session during week 7 workshop
        """
        # add the '$' character to the end of the string
        text = text + '$'

        # initialize the i and j pointers
        i = 0
        j = 0

        # length of the string
        n = len(text)

        # start iterating through the string
        while i <= n:
            
            # if i is incremented, then the end class end pointer will be incremented
            # trick 1
            self.end.extend()
            self.previous_node = None

            # O(N)
            while j < i:

                # If the active node is root, then the active length will be i-j
                if self.active_node == self.root:

                    # we can keep track of the length even if the j is frozen and only i is incremented
                    self.active_length  = i-j
                
                # get the node where the active node should be
                # implementation trick 2 which is the skip count trick
                self.skip_count(text, i, self.active_node, self.active_length)

                # get the character of the active edge
                # minus 36 so that the ascii value between [37,126] and '$' can be 0-indexed
                char_rem = ord(text[i - self.active_length]) - 36

                # get the active edge
                active_edge = self.active_node[char_rem]
                
                # if the current char does not exist in the active node
                # means that the suffix does not exist in the tree
                if active_edge is None:

                    # create new edge
                    self.active_node[char_rem] =  Node(i - self.active_length, self.end, suffix_link= self.root, leaf_node = True)   
                    self.active_node[char_rem].j = j
                
                # if the current pointer char is different than the char in the active edge
                elif text[i-1] != text[active_edge.start + self.active_length-1]:
                    
                    # create a node representing the current edge with a different end
                    existing_char_node = Node(active_edge.start, active_edge.start + self.active_length - 1, suffix_link = self.root)

                    # re-add the current edge to the active node
                    self.active_node[char_rem] = existing_char_node

                    # index for the existing node
                    continue_index = ord(text[active_edge.start - 1 + self.active_length ]) - 36   

                    # start value for existing node
                    active_edge.start += self.active_length -1       

                    # add the existing node to the current edge                 
                    existing_char_node[continue_index] = active_edge   

                    # creating the new node
                    # new node is the node that the new char will be added to
                    new_node_index = ord(text[i - 1]) - 36     
                    existing_char_node[new_node_index] = Node(i-1, self.end, leaf_node = True, suffix_link=self.root)  
                    existing_char_node[new_node_index].j = j    

                # trick 3, which is the showstopper trick
                else:

                    # if the i matches, then freeze the j pointer
                    break

                j += 1      
                # go to the suffix link                                                
                self.active_node = self.active_node.suffix_link             

            # increment the i pointer
            i += 1                   
            self.active_length += 1  
                


    def skip_count(self, text: str, current_pointer: int, a_node: Node, a_length: int) -> Node:
        """
        Returns the node where the active node should be. This is used for the skip count trick
        and represents the traversal() method in the pseudocode found in week 4's lecture note.

        Input:
        :text           : a string
        :end            : the pointer of the string
        :a_node         : the active node
        :a_length       : the length of the active edge

        Time complexity: 
            :Worst          : O(N), where n is the length of the string
        Space complexity:
            :Aux            : O(1)
        """

        # O(N) worst case
        while True:

            # If the active length is 0, or the current node is leaf, then return the current node.
            # This means that there is no need to traverse to the node deeper in the tree.
            if a_length == 0 or a_node.is_leaf():
                return a_node
            
            # If traversal is possible or needed, then update the current node and length.
            self.active_node = a_node
            self.active_length = a_length

            # To get the first character in the active edge
            # Used for indexing so that it could access the node
            lastj_index = ord(text[current_pointer - a_length]) - 36

            # Get the edge corresponding to the character.
            edge = a_node[lastj_index]

            # If the edge is None, then the corresponding edge is not yet created
            # Will be created in the ukkonen algorithm                                 
            if edge is None:            
                return a_node 

            # If it is still possible to traverse through the edge, then return the node
            if edge.get_length() > a_length:
                return a_node

            # Means not possible to traverse through the edge since the length of the edge is less than the active length.
            # So, move to a new node and update the active length
            else:
                a_node =  edge
                a_length = a_length - edge.get_length()

    def get_suffix_tree(self):
        """
        Returns the suffix tree in the form of a list. Uses the get_suffix_tree_aux() method.

        :Complexity:
        :Time           : O(N), where N is the length of the string
        :Aux Space      : O(N), where N is the length of the string
        """
        suffix_tree = []
        return self.get_suffix_tree_aux(self.root, suffix_tree)

    def get_suffix_tree_aux(self, node: Node, suffix_tree: list):
        """
        Goes through the suffix tree using inorder traversal and returns the suffix tree in the form of a list.
        """

        # if the node is a leaf node, then append the j.
        if node.is_leaf():
            # plus one because the result format is 1-indexed
            suffix_tree.append(node.j + 1)

        # if the node is not a leaf node
        else:

            # use in order traversal to go deeper into the tree until it reaches a leaf node
            for child in node.child_nodes:

                # if the child node is not None, then use recursion to go deeper into the tree 
                # or to add in the list if it is a leaf node
                if child is not None:
                    # keep recursing until it reaches a leaf node
                    self.get_suffix_tree_aux(child, suffix_tree)

        return suffix_tree


