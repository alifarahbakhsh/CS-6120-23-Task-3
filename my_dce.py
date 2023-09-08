import json
import sys

def get_basic_blocks(_code):
	blocks = dict()
	for func in _code["functions"]:
		blocks[func["name"]] = []
		new_block = []
		fun_len = len(func["instrs"]) - 1
		for instr_idx, instr in enumerate(func["instrs"]):
			if "label" in instr:
				if not new_block == []:
					blocks[func["name"]].append(new_block)
				new_block = [instr]
				continue
			new_block.append(instr)
			if is_breaking_block(instr):
				blocks[func["name"]].append(new_block)
				new_block = []
				continue
			if instr_idx == fun_len:
				blocks[func["name"]].append(new_block)
				new_block = []
				continue
		if not new_block == []:
			blocks[func["name"]].append(new_block)
	return blocks
		

def is_breaking_block(_instr):
	is_breaking = False
	if _instr["op"] == "jmp" or _instr["op"] == "br" or _instr["op"] == "ret":
		is_breaking = True
	return is_breaking

def dce(_blocks):
	for func_idx, func in enumerate(_blocks):
		for block_idx, block in enumerate(_blocks[func]):
			not_used_vars = []
			for instr_idx, instr in enumerate(reversed(block)):
				l = len(block)
				if "dest" in instr:
					if instr["dest"] in not_used_vars:
						del _blocks[func][block_idx][l - instr_idx - 1]
						#del _code["functions"][func_idx]["instrs"][l - instr_idx]
						continue
					else:
						not_used_vars.append(instr["dest"])
					#print(instr)
				if "args" in instr:
					for arg in instr["args"]:
						if arg in not_used_vars:
							idx = not_used_vars.index(arg)
							del not_used_vars[idx]
						if not arg in not_used_vars:
							pass
				#print(instr)
	return _blocks

def convert_to_Bril(_blocks, _org_code):
	opt_code = {}
	opt_code["functions"] = []
	funcs = list(_blocks.keys())
	for func_idx, func in enumerate(funcs):
		new_func = {}
		new_func["name"] = func
		if "args" in _org_code["functions"][func_idx]:
			new_func["args"] = _org_code["functions"][func_idx]["args"]
		if "type" in _org_code["functions"][func_idx]:
			new_func["type"] = _org_code["functions"][func_idx]["type"]
		
		instrs = []
		for _block in _blocks[func]:
			instrs = instrs + _block
		new_func["instrs"] = instrs
		opt_code["functions"].append(new_func)
	return opt_code
		

if __name__ == "__main__":
	code = json.load(sys.stdin)
	blocks = get_basic_blocks(code)
	#print(blocks)
	output = dce(blocks)
	#print("after")
	#print(output)
	output = convert_to_Bril(output, code)
	#print("Output is")
	#print(output)
	json.dump(output, sys.stdout, indent=2, sort_keys=True)
	
