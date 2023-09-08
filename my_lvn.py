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

def lvn(_blocks, _code):
	for func_idx, func in enumerate(_blocks):
		i = 0
		for block_idx, block in enumerate(_blocks[func]):
			env2tab = dict()
			vals = []
			vars = []
			for instr_idx, instr in enumerate(block):
				#print(instr)
				tup = ("-", [])
				if "op" in instr and instr["op"] == "alloc":
					continue
				if "dest" in instr and instr["type"] == "float":
					continue
				if not "args" in instr:
					if "op" in instr and instr["op"] == "const":
						if instr["type"] == "bool" and instr["value"] == False:
							tup[1].append("False")
						elif instr["type"] == "bool" and instr["value"] == True:
							tup[1].append("True")
						else:
							tup[1].append(instr["value"])
						#print(f"tup is {tup}")
						is_in, idx = is_in_table(tup, vals)
						if is_in:
							env2tab[instr["dest"]] = idx
						else:
							env2tab[instr["dest"]] = len(vals)
							vals.append(tup)
							vars.append(instr["dest"])
					continue
				if "dest" in instr:
					if instr["op"] == "call":
						tup = (instr["op"]+"-"+instr["funcs"][0], tup[1])
					else:
						tup = (instr["op"], tup[1])
					is_sortable = True
					for arg in instr["args"]:
						if arg in env2tab:
							tup[1].append(env2tab[arg])
						else:
							tup[1].append(arg)
							is_sortable = False
							# is_func_arg = False
							# if "args" in _code["functions"][func_idx]:
							# 	print("Has args")
							# 	print(arg)
							# 	#print(_code["functions"][func_idx]["args"])
							# 	for tmp_idx, tmp_arg in enumerate(_code["functions"][func_idx]["args"]):
							# 		if arg == tmp_arg["name"]:
							# 			print("found one!")
							# 			#print(arg)
							# 			tup[1].append(-1 - tmp_idx)
							# 			is_func_arg = True
							# 			break
					if is_sortable:	
						tup[1].sort()
					#print(f"tup is {tup}")
				is_in, idx = is_in_table(tup, vals)
				#print(f"is_in is {is_in} and idx is {idx}")
				if is_in:
					env2tab[instr["dest"]] = idx
				else:
					if "dest" in instr:
						if instr["op"] == "id" and (instr["args"][0] in env2tab):
							env2tab[instr["dest"]] = env2tab[instr["args"][0]]
							vals.append(tup)
							vars.append(instr["dest"])
						else:
							env2tab[instr["dest"]] = len(vals)
							vals.append(tup)
							vars.append(instr["dest"])

				for arg_idx, _ in enumerate(instr["args"]):
					if instr["args"][arg_idx] in env2tab:
						_blocks[func][block_idx][instr_idx]["args"][arg_idx] = vars[env2tab[instr["args"][arg_idx]]]
				#print("new instr is")
				#print(instr)
			#print(f"block number {i}")
			i += 1
			#print(env2tab)
			#print(vals)
			#print(vars)
			for instr_idx, instr in enumerate(block):
				if not "args" in instr:
					continue

	return _blocks

def is_in_table(_tup, _vals):
	is_in = False
	where = 0
	for idx, val in enumerate(_vals):
		#print(f"in for ---- tup is {_tup}, val is {val}")
		if is_equal(_tup, val):
			is_in = True
			where = idx
			break
	return is_in, where

def is_equal(_tup, _val):
	#for idx, elm in enumerate(_val[1]):
	#	if idx < len(_tup[1]):
	#		if (_tup[1][idx] == 0 and elm == False) or (_tup[1][idx] == 1 and elm == True):
	#			return False
	#	else:
	#		break
	return _tup == _val

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
    output = lvn(blocks, code)
    output = convert_to_Bril(output, code)
    #print(output)
    json.dump(output, sys.stdout, indent=2, sort_keys=True)
	
