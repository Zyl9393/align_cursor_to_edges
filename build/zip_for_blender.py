# This file must be run from the repository root.

projectName = "align_cursor_to_edges"
additionalDirectories = []
additionalFiles = ["LICENSE"]

def getVersion():
	import re
	with open("__init__.py", mode="r") as f:
		m = re.compile(r'^\s*"version"\s*:\s*\(\s*(?P<major>\d+)\s*,\s*(?P<minor>\d+)\s*(,\s*(?P<patch>\d+)\s*)?\)\s*,?\s*$', re.MULTILINE).search(f.read())
		if m.group("patch") != None:
			return f'{m.group("major")}.{m.group("minor")}.{m.group("patch")}'
		else:
			return f'{m.group("major")}.{m.group("minor")}'

if __name__ == "__main__":
	import zipfile
	from pathlib import Path
	zipFileName = f"{projectName}-{getVersion()}.zip"
	print(f"Writing {zipFileName}...")
	with zipfile.ZipFile(zipFileName, "w", zipfile.ZIP_DEFLATED) as zf:
		for dir in additionalDirectories:
			for path in Path(dir).rglob("*"):
				arcName = f"{projectName}/{path.as_posix()}"
				print(f"Adding {path} as {arcName}")
				zf.write(path, arcName)
		for path in Path(".").glob("*.py"):
			arcName = f"{projectName}/{path.as_posix()}"
			print(f"Adding {path} as {arcName}")
			zf.write(path, arcName)
		for fileName in additionalFiles:
			arcName = f"{projectName}/{fileName}"
			print(f"Adding {fileName} as {arcName}")
			zf.write(fileName, arcName)
