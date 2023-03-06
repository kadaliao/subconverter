import glob
import os, sys

MAIN_IMAGE_NAME="tindy2013/subconverter"
TARGET_TAG="latest" if len(sys.argv) < 2 else sys.argv[1]

args = [f"docker manifest create {MAIN_IMAGE_NAME}:{TARGET_TAG}"]
for i in glob.glob("/tmp/images/*/*.txt"):
    with open(i, "r") as file:
        args += f" --amend {MAIN_IMAGE_NAME}@{file.readline().strip()}"
cmd_create="".join(args)
cmd_push = f"docker manifest push {MAIN_IMAGE_NAME}:{TARGET_TAG}"
os.system(cmd_create)
os.system(cmd_push)
