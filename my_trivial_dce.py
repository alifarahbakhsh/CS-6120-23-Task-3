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

def dce(_code):
	for func_idx, func in enumerate(_code["functions"]):
		defs = []
		uses = []
		for instr_idx, instr in enumerate(func["instrs"]):
			if "dest" in instr:
				defs.append(instr["dest"])
			if "args" in instr:
				for arg in instr["args"]:
					if not arg in uses:
						uses.append(arg)
		for instr_idx, instr in enumerate(func["instrs"]):
			if "dest" in instr:
				if not instr["dest"] in uses:
					del _code["functions"][func_idx]["instrs"][instr_idx]
	return _code
			
				

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
	output = dce(code)
	#print("after")
	#print(output)
	#print("Output is")
	#print(output)
	json.dump(output, sys.stdout, indent=2, sort_keys=True)
	
