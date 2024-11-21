import os
from ruamel.yaml import YAML, yaml_object

yaml=YAML()
yaml.preserve_quotes = True
yaml.default_flow_style = False
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.width = 9999

class MultiDictDuplicateKeyError(Exception):
    pass

@yaml_object(yaml)
class MultiDict(dict):
    """ no support for deletion of keys """
    yaml_tag = '!MultiDict'

    def __init__(self, *args, **kw):
        self.__duplicate__ = []
        if args and not isinstance(args[0], dict):
            dict.__init__(self, **kw)
            for arg in args[0]:
                self[arg[0]] = arg[1]
        else:
            dict.__init__(self, *args, **kw)

    def __setitem__(self, key, value):
        if key in self:
            if key in self.__duplicate__:  # it should already be a list
                dict.__getitem__(self, key).append(value)
            else:
                self.__duplicate__.append(key)
                dict.__setitem__(self, key, [dict.__getitem__(self, key), value])
        else:
             dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        if key in self.__duplicate__:
            raise MultiDictDuplicateKeyError("should use multival(key)")
        return dict.__getitem__(self, key)

    def multival(self, key):
        assert key in self.__duplicate__
        values = dict.__getitem__(self, key)
        assert isinstance(values, list)
        for value in values:
             yield value

    def __str__(self):
        return repr({('__duplicate__' + repr(k) if k in self.__duplicate__ else k): v
                    for k, v in self.items()})

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_sequence(cls.yaml_tag, [node.__duplicate__, dict(node)])

    @classmethod
    def from_yaml(cls, constructor, node):
        # necessary to deal with recursive data structures
        for y in constructor.construct_yaml_map(node.value[1]):
            pass
        for dup in constructor.construct_yaml_seq(node.value[0]):
            pass
        ret = cls(y)
        ret.__duplicate__ = dup
        return ret

def process_yaml_files(directory):
    # Iterate through all files in the specified directory
    for filename in os.listdir(directory):
        # Check if the file has a .yaml or .yml extension
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            file_path = os.path.join(directory, filename)

            # Open and load the YAML file
            with open(file_path, 'r') as file:
                data = MultiDict(yaml.load(file))

            print(type(data))

            # Write the data back to the same file
            with open(file_path, 'w') as file:
                yaml.dump(data, file)

if __name__ == "__main__":
    # Specify the directory containing the YAML files
    directory = '.'

    # Process the YAML files in the specified directory
    process_yaml_files(directory)
