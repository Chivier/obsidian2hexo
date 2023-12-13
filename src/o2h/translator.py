import re
import argparse
import sys
import os
import json
import glob
import mimetypes
import datetime
import subprocess
import shutil

mimetypes.init()

# Some Limits:
# This tool can only deal with some simple situation, all including files should be written in a standalone line

# Read config filepython -m build
## Input:
## - config file path
## Output:
## - list of obsidian home paths
def getConfigurations(config_file_path=""):
    if len(config_file_path) == 0:
        # TODO: add Windows config file path
        config_file_path = os.path.expanduser("~") + "/.config/o2h/config.json"

    if os.path.isfile(config_file_path):
        # open JSON file
        config_file = open(config_file_path, "r")
        # read date from file
        data = json.loads(config_file.read())
        return data
    else:
        print("Config file not found")
        exit(0)


class translator_tp:
    def __init__(self):
        self.config = None
        self.output = "/tmp/o2houtput"
        self.input = None
        self.tags = []
        self.links = []
        self.date = []
        self.time = None
        self.category = None
        self.title = ""
        self.picgo = False

    def get_file_type(self, file_name: str):
        mimestart = mimetypes.guess_type(file_name)[0].lower()
        mime_parse = mimestart.split("/")
        if mime_parse[0] == "image":
            return "image"
        if mime_parse[1] == "pdf":
            return "pdf"
        return "undefined"

    def get_file_type_detail(self, file_name: str):
        mimestart = mimetypes.guess_type(file_name)[0].lower()
        mime_parse = mimestart.split("/")
        return mime_parse[1]

    def create_result_folder(self):
        # Check if directory exists
        if not os.path.isdir(self.output):
            os.mkdir(self.output)
        # If directory is not empty
        if len(os.listdir(self.output)) != 0:
            shutil.rmtree(self.output)
            os.mkdir(self.output)

    def read_and_find_info(self):
        tag_pattern = r"#[^\ ^#^\s]+"
        link_pattern = r"\!\[\[.+\]\]"

        # Find all links and tags in an obsidian file
        with open(self.input, "r") as file:
            line_index = 0
            for line in file:
                if line_index <= 10:
                    tag_list = re.findall(tag_pattern, line)
                
                link_list = re.findall(link_pattern, line)
                if len(tag_list) > 0:
                    if len(self.tags) == 0:
                        self.tags = tag_list
                    else:
                        self.tags += tag_list
                if len(link_list) > 0:
                    if len(self.links) == 0:
                        self.links = link_list
                    else:
                        self.links += link_list
                
                line_index += 1
            file.close()
        # Remove first '#' from the beginning of the line
        for index in range(len(self.tags)):
            self.tags[index] = self.tags[index][1:].split("/")[-1]
        self.tags = list(set(self.tags))

        # Update time as last modified time
        file_modify_date = (
            str(datetime.datetime.fromtimestamp(os.path.getmtime(self.input)))
            .split(" ")[0]
            .split("-")
        )
        self.time = str(
            datetime.datetime.fromtimestamp(os.path.getmtime(self.input))
        ).split(".")[0]
        self.date = [int(item) for item in file_modify_date]

        # Get filename as title
        self.title = self.input.split("/")[-1].split(".")[0]

    def handle_property(self):
        property_pattern = r"---"
        property_name_patter = r"^[^:]*:"
        property_item_patter = r"[\t ]*-[\t ]*"
        
        with open(self.input, "r") as file:
            for line in file:
                # if first line is not property, then return
                if not re.match(property_pattern, line):
                    print("This file has no property")
                    return 0
                else:
                    break

        property_count = 0
        with open(self.input, "r") as file:
            property_item = False
            property_name = ""
            property_start = -1

            for line in file:
                if re.match(property_pattern, line):
                    if property_start == -1:
                        property_start = 1
                        continue
                    if property_start == 1:
                        break
                if property_item:
                    if re.match(property_item_patter, line):
                        line = line.strip()
                        line = line[2:]
                        line = line.strip()
                        if property_name == "tags" or property_name == "tag":
                            self.tags.append(line)
                        
                        continue
                if re.match(property_name_patter, line):
                    property_count += 1
                    property_item = False
                    line = line.strip()
                    property_parse = line.split(":", 1)
                    property_name = property_parse[0]
                    # property_value = property_parse[1]
                    if property_name == "tags" or property_name == "tag":
                        property_item = True
                    continue
                
                

    def get_file_location(self, name):
        """
        finds the location of a file in obsidian
        Args:
         - self, name

        Return:
         - file_paths[0]
        """
        name = name[3:-2].replace(" ", " ")
        target_base = self.config["obsidian_target"]
        file_paths = []
        # searches for findpath in the target base directory
        for findpath in target_base:
            bashCommand = ["find", findpath, "-name", f"*{name}*"]
            # print(bashCommand)
            process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE)
            output, error = process.communicate()
            file_paths = list(output.decode("utf-8").split("\n"))
            # print(output)
            if len(file_paths) > 0:
                break
        if len(file_paths) == 0:
            print("Cannot find file in path")
            exit(0)
        return file_paths[0]

    def translate(self):
        attributes_pattern = r"^---$"
        tag_pattern = r"#[^\ ^#^\s]+"
        link_pattern = r"\!\[\[.+\]\]"
        output_file_name = self.output + "/" + self.title.replace(" ", "-") + ".md"
        output_dir_name = self.output + "/" + self.title.replace(" ", "-")

        if not self.picgo:
            os.mkdir(output_dir_name)
        output_file = open(output_file_name, "w")

        info_header = "---\n"
        # title info
        info_header += "title: " + self.title + "\n"
        # date info
        info_header += "date: " + self.time + "\n"
        # layout info
        info_header += "layout: " + "'[post]'" + "\n"
        # tags info
        info_header += "tags:\n"
        for tag in self.tags:
            info_header += "  - " + tag + "\n"
        # categories info
        info_header += "categories:\n"
        info_header += "  - " + self.category + "\n"
        # toc info
        info_header += "toc: true\n"
        info_header += "---\n"

        image_counter = 0
        pdf_counter = 0

        output_file.write(info_header)

        more_tag = False
        with open(self.input) as input_file:
            has_attribute = False
            attributes_end = False
            initial_line = True
            for line in input_file:
                # Skip properties
                if initial_line:
                    initial_line = False
                    if re.match(attributes_pattern, line.strip()):
                        has_attribute = True
                        continue
                if has_attribute and not attributes_end:
                    if re.match(attributes_pattern, line.strip()):
                        attributes_end = True
                        continue
                    else:
                        continue

                if re.match(tag_pattern, line):
                    # tag is handled before
                    continue
                if re.match(link_pattern, line):
                    # add a new link here
                    link_file_name = re.findall(link_pattern, line)[0]
                    link_file_location = self.get_file_location(link_file_name)
                    link_file_location = link_file_location.replace(" ", " ")
                    link_file_type = self.get_file_type(link_file_location)
                    if link_file_type == "undefined" or link_file_type == "pdf":
                        # do not care about undefined files
                        continue
                    elif link_file_type == "image":
                        if self.picgo:
                            # get detail type of an image
                            detailed_type = self.get_file_type_detail(link_file_location)
                            image_counter += 1
                            bashCommand = ["picgo", "upload", link_file_location]
                            process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE)
                            output, error = process.communicate()
                            output = output.decode("utf-8")
                            # print(output.find("SUCCESS"))
                            if output.find("SUCCESS") != -1:
                                # Find success info
                                success_info = output.split("\n")
                                # print(success_info)
                                target_file_name = ""
                                success_info_index = len(success_info)
                                while success_info_index >= 0:
                                    success_info_index -= 1
                                    if success_info[success_info_index].find("SUCCESS")!= -1:
                                        target_file_name = success_info[success_info_index + 1]
                                output_file.write(
                                    f'<img src="{target_file_name}" width="80%" height="80%">\n'
                                )
                            else:
                                sys.stderr.write("Picgo upload failed\n")
                                exit(0)
                        else:
                            # get detail type of an image
                            detailed_type = self.get_file_type_detail(link_file_location)
                            image_counter += 1
                            target_file_name = f"image{image_counter}.{detailed_type}"
                            target_file_location = output_dir_name + "/" + target_file_name
                            bashCommand = ["cp", link_file_location, target_file_location]
                            process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE)
                            output, error = process.communicate()
                            # print out image link here
                            output_file.write(
                                f'<img src="{target_file_name}" width="80%" height="80%">\n'
                            )
                    # elif link_file_type == "pdf":
                    #     pdf_counter += 1
                    #     target_file_name = f"pdf{pdf_counter}.pdf"
                    #     target_file_location = output_dir_name + "/" + target_file_name
                    #     bashCommand = ["cp", link_file_location]
                    #     process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE)
                    #     output, error = process.communicate()
                    #     # print out pdf link here
                    #     output_file.write(
                    #         str("{" + f"% pdf ./{target_file_name} \%" + "}\n")
                    #     )
                else:
                    # Common Line
                    if len(line) == 1:
                        output_file.write(line)
                        continue
                    else:
                        if more_tag is False:
                            output_file.write(line)
                            output_file.write("\n<!--more-->\n\n")
                            more_tag = True
                        else:
                            output_file.write(line)


def o2h():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="get the obs markdown filename", type=str)
    parser.add_argument(
        "-o", "--output", type=str, help="get output dir", default="/tmp/o2houtput"
    )
    parser.add_argument(
        "-c", "--category", type=str, help="get category", default="Skill"
    )
    parser.add_argument(
        "-p", "--picgo", help="use picgo", action=argparse.BooleanOptionalAction
    )
    args = parser.parse_args()
    if str(args.filename)[-3:] != ".md":
        print("This is not a .md file")
        return 0

    vm = translator_tp()
    vm.input = args.filename
    vm.output = args.output
    vm.category = args.category
    vm.picgo = args.picgo
    vm.name = vm.input.split("/")[-1][0:-3]
    vm.config = getConfigurations()

    vm.create_result_folder()
    vm.read_and_find_info()
    vm.handle_property()
    vm.translate()
    return 1

if __name__ == "__main__":
    o2h()
