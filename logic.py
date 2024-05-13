#Author : _hdrien
#404CTF 2024

import json

class Gate:
    def __init__(self, name, operation, mask):
        self.name = name
        self.operation = operation
        self.mask = mask
    
    def __str__(self):
        return f"{self.name} {self.mask}"

    def output(self, input):
        modified_bits = self.operation([input[i] for i in self.mask])
        output = list(input)
        for i in range(len(self.mask)):
            output[self.mask[i]] = modified_bits[i]
        return tuple(output)
    
    def to_c_code(self, var_name):
        # implemented in subclasses
        pass


class NGATE(Gate):
    arity = 1
    def __init__(self, mask):
        op = lambda x: (x[0] ^ 1,)
        super().__init__("NOT", op, mask)

    def to_c_code(self, var_name):
        return f"{var_name} ^= {1 << self.mask[0]};"

class CGATE(Gate):
    arity = 2
    def __init__(self, mask):
        op = lambda x: (x[0], x[0]^x[1])
        super().__init__("CNOT", op, mask)

    def to_c_code(self, var_name):
        return f"{var_name} ^= ((({var_name} >> {self.mask[0]}) & 1) << {self.mask[1]});"

class TGATE(Gate):
    arity = 3
    def __init__(self, mask):
        op = lambda x: (x[0], x[1], x[2]^(x[1]&x[0]))
        super().__init__("TOFFOLI", op, mask)
    
    def to_c_code(self, var_name):
        return f"{var_name} ^= ((({var_name} & {1 << self.mask[0]}) >> {self.mask[0]}) & (({var_name} & {1 << self.mask[1]}) >> {self.mask[1]})) << {self.mask[2]};"

class Circuit:
    def __init__(self, gates, bits):
        self.gates = gates
        self.bits = bits
        self.truth_table = self.truth_table()
        self.hash = hash(self.truth_table)
    
    def __eq__(self, other):
        if other==None:
            return False
        return self.hash == other.hash

    def __str__(self):
        return str([str(gate) for gate in self.gates])

    def output(self, input):
        for gate in self.gates:
            input = gate.output(input)
        return input

    def truth_table(self):
        table = []
        for i in range(2**self.bits):
            input = tuple(int(c) for c in bin(i)[2:].zfill(self.bits))
            table.append((input,(self.output(input))))
        return tuple(table)
    
    def to_c_code(self, var_name, tab_level=0):
        code = ""
        for gate in self.gates:
            code += "\n"+"\t"*tab_level + gate.to_c_code(var_name)
        return code
    
    def to_json(self):
        return json.dumps({"gates": [[gate.name, gate.mask] for gate in self.gates], "bits": self.bits})
    
    def inverse(self):
        return Circuit(self.gates[::-1], self.bits)

def circuit_from_json(json_str):
    json_dict = json.loads(json_str)
    gates = []
    for gate_name, mask in json_dict["gates"]:
        if gate_name == "NOT":
            gates.append(NGATE(mask))
        elif gate_name == "CNOT":
            gates.append(CGATE(mask))
        elif gate_name == "TOFFOLI":
            gates.append(TGATE(mask))
    return Circuit(gates, json_dict["bits"])

# circuit1 = Circuit([TGATE([0,1,2]), NGATE([0]), TGATE([0,1,2]), NGATE([0])], 3)
# circuit2 = Circuit([CGATE([1,2])], 3)
# print(circuit1==circuit2)
# print(CGATE([2,3]).to_c_code("input"))
# print(TGATE([3,1,1]).to_c_code("input"))
    



