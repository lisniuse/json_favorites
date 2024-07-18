import os
import zipfile
import json
import subprocess
import webbrowser
import locale
import shutil
import sys

# version
VERSION = "1.0.1"

# modules supported
MODULES = [ "github", "tools", "website" ]

class LocaleHandler:
    translations = {
        "en": {
            "file_not_found": "No exe or zip file was found from your hard drive. Please download it yourself according to the download address provided.",
            "input_tips": "Enter command(Enter 'help' to see the help):",
            "keyword_required": "Keyword to search for",
            "type_optional": "Category type to search (e.g., tools, website, github). If not specified, search all categories",
            "no_matches": "No matching items found.",
            "enter_choice": "Enter the number to open, or 0 to return: ",
            "invalid_input": "Invalid input.",
            "invalid_selection": "Invalid selection.",
            "no_url": "No URL found for the selected item.",
            "execution_failed": "Failed to execute the tool: ",
            "no_exe_path": "No executable path found for the selected item.",
            "help": """
Welcome to JsonFavorites! Source code available at: https://github.com/lisniuse/json_favorites

Available commands:
1. find - Search for items based on a keyword and optional category.
   Usage: find -k <keyword> [-t <category>]

2. list - List all items, optionally filtered by category.
   Usage: list [-t <category>]

3. help - Show this help message.
   Usage: help

4. Enter the number to open the item, or 0 to return to the menu.
   Note: If you enter 0, you will return to the command prompt without making a selection.

Examples:
- Find items related to 'Python':
  find -k Python

- List all items in the 'website' category:
  list -t website

- Show this help message:
  help
            """,
        },
        "zh": {
            "file_not_found": "没有从你的硬盘里找到任何exe或者zip文件，请根据提供的下载地址自行下载。",
            "input_tips": "Enter command（help可查看帮助）：",
            "keyword_required": "要搜索的关键字",
            "type_optional": "要搜索的类别类型（例如：tools, website, github）。如果未指定，则搜索所有类别",
            "no_matches": "未找到匹配的项目。",
            "enter_choice": "输入编号进行打开，或输入 0 返回: ",
            "invalid_input": "输入无效。",
            "invalid_selection": "选择无效。",
            "no_url": "所选项目没有找到 URL。",
            "execution_failed": "工具执行失败：",
            "no_exe_path": "所选项目没有找到可执行路径。",
            "help": """
欢迎使用 JsonFavorites！源码地址：https://github.com/lisniuse/json_favorites

可用的命令：
1. find - 根据关键字和可选类别搜索项目。
   用法：find -k <keyword> [-t <category>]

2. list - 列出所有项目，可按类别筛选。
   用法：list [-t <category>]

3. help - 显示帮助信息。
   用法：help

4. 输入编号以打开项目，或输入 0 返回菜单。
   注意：如果输入 0，你将返回到命令提示符，而不选择任何项目。

示例：
- 查找与 'Python' 相关的项目：
  find -k Python

- 列出所有属于 'website' 类别的项目：
  list -t website

- 显示帮助信息：
  help
            """,
        }
    }

    def __init__(self):
        """Initialize the locale handler with the appropriate translations."""
        self.locale_texts = self.get_locale()

    def get_locale(self):
        """Get the system locale and return the appropriate translation dictionary."""
        lang, _ = locale.getlocale()
        if lang and lang.startswith("Chinese"):
            return self.translations["zh"]
        else:
            return self.translations["en"]

class StringFormatter:
    @staticmethod
    def count_chinese_characters(s):
        """Count the number of Chinese characters in a string."""
        count = 0
        for char in s:
            if '\u4e00' <= char <= '\u9fff':
                count += 1
        return count

    @staticmethod
    def calculate_display_width(s):
        """Calculate the display width of a string, assuming Chinese characters are twice the width of English characters."""
        width = 0
        for char in s:
            if '\u4e00' <= char <= '\u9fff':
                width += 2
            else:
                width += 1
        return width

    @staticmethod
    def truncate_string(s, max_width):
        """Truncate a string to fit within a given width, assuming Chinese characters are twice the width of English characters."""
        if StringFormatter.calculate_display_width(s) <= max_width:
            return s
        truncated = ''
        width = 0
        for char in s:
            char_width = 2 if '\u4e00' <= char <= '\u9fff' else 1
            if width + char_width > max_width - 3:
                return truncated + '...'
            truncated += char
            width += char_width
        return truncated

    @staticmethod
    def desc_indent(name, max_name_width):
        """Calculate the indent for the description based on the name width."""
        return max_name_width - StringFormatter.count_chinese_characters(name)

class JsonBookmarkTool:
    def __init__(self, locale_handler, string_formatter):
        """Initialize the JSON Bookmark Tool with locale and string formatter handlers."""
        self.locale_handler = locale_handler
        self.string_formatter = string_formatter

    def find_files(self, directory, extension=".json"):
        """Find all files in the given directory and its subdirectories with the specified extension."""
        file_paths = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(extension):
                    file_paths.append(os.path.join(root, file))
        return file_paths

    def load_json_files(self, file_paths):
        """Load JSON data from the list of file paths."""
        json_data = {}
        for m in MODULES: json_data[m] = []
        
        for file_path in file_paths:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                for key in data:
                    if key in MODULES:
                        for item in data[key]:
                            item["sourceFile"] = file_path
                            json_data[key].append(item)
        return json_data

    def search_items(self, json_data, keyword, category=None):
        """Search for items in JSON data that match the given keyword and optionally a category."""
        matches = []
        for m in json_data:
            if category and m != category:
                continue
            for item in json_data[m]:
                if keyword.lower() in json.dumps(item, ensure_ascii=False).lower():
                    matches.append((m, item))
        return matches

    def list_items(self, json_data, category=None):
        """List all items in JSON data optionally filtered by category."""
        items = []
        for m in json_data:
            print(m, category)
            if category and m != category:
                continue
            for item in json_data[m]:
                items.append((m, item))
        return items

    def display_results(self, results):
        """Display the search results in a formatted way with aligned columns and truncated descriptions."""
        terminal_width = shutil.get_terminal_size().columns
        
        max_type_width = max(self.string_formatter.calculate_display_width(item[0]) for item in results)
        max_name_width = max(self.string_formatter.calculate_display_width(item[1].get('name', '')) for item in results)
        
        available_desc_width = terminal_width - (10 + max_type_width + max_name_width + 4)
        if available_desc_width <= 0:
            available_desc_width = 20

        print(f"{'Index':<5} [{'type':<{max_type_width}}] {'name':<{max_name_width}} {'desc'}")
        print('-' * (10 + max_type_width + max_name_width + available_desc_width + 4))

        for idx, (category, item) in enumerate(results, start=1):
            desc = item.get('remarks', '') or item.get('desc', '')
            name = item.get('name', '')
            desc = self.string_formatter.truncate_string(desc, available_desc_width - 1)
            indent = self.string_formatter.desc_indent(name, max_name_width)
            print(f"{idx:<5} [{category:<{max_type_width}}] {name:<{indent}} {desc}")

    def parse_arguments(self, input_command):
        """Parse the user command from input."""
        locale_texts = self.locale_handler.locale_texts
        input_command = input_command.lower()
        args = input_command.split()
        if not args:
            return None, None, None
        
        command = args[0] if len(args) > 0 else 'list'
        keyword = None
        category = None

        if command == 'help':
            return command, None, None
        
        if command == 'v' or command == '-v' or command == 'version':
            return command, None, None

        if command not in ['find', 'list']:
            print(locale_texts["invalid_input"])
            return None, None, None
        
        if command == 'find':
            if '-k' in args:
                keyword_index = args.index('-k') + 1
                if keyword_index < len(args):
                    keyword = args[keyword_index]
                else:
                    print(locale_texts["keyword_required"])
                    return None, None, None
            else:
                print(locale_texts["keyword_required"])
                return None, None, None

        if '-t' in args:
            type_index = args.index('-t') + 1
            if type_index < len(args):
                category = args[type_index]
        
        return command, keyword, category

    def load_json_data(self, directory):
        """Load JSON data from the specified directory."""
        file_paths = self.find_files(directory)
        return self.load_json_files(file_paths)
    
    def display_help(self):
        """Display help information in the appropriate language."""
        help_text = self.locale_handler.locale_texts.get("help", "")
        print(help_text)

    def execute_command(self, command, keyword, category, json_data):
        """Execute the specified command (find, list, or help) and return the results."""
        locale_texts = self.locale_handler.locale_texts
        if command == "v" or command == '-v' or command == 'version':
            print("current version: ", VERSION);
            return []
        elif command == 'find':
            return self.search_items(json_data, keyword, category)
        elif command == 'list':
            return self.list_items(json_data, category)
        elif command == 'help':
            self.display_help()
            return []
        else:
            print(locale_texts["invalid_input"])
            return []

    def handle_github_or_website(self, selected_item):
        """Handle and display detailed information for 'github' or 'website' categories."""
        url = selected_item.get("url")
        if url:
            print(f"URL: {url}")
            webbrowser.open(url)
        else:
            print(self.locale_handler.locale_texts["no_url"])
    
    def run_exe(self, exe_path):
      if not os.path.exists(exe_path):
        return
      
      # Try to execute the tool
      if exe_path:
          print(f"Executable Path: {exe_path}")
          try:
              # Ensure the executable path exists
              if os.path.isfile(exe_path):
                  subprocess.Popen([exe_path], shell=True)
              else:
                  print(f"Executable file does not exist: {exe_path}")
          except Exception as e:
              print(f"Failed to start executable: {e}")
      else:
          print(self.locale_handler.locale_texts["no_exe_path"])
    
    def un_zip(self, zip_path):
      if not os.path.exists(zip_path):
        return
      
      extract_dir = os.path.dirname(zip_path)
      
      try:
          with zipfile.ZipFile(zip_path, 'r') as zip_ref:
              zip_ref.extractall(extract_dir)
              print(f"Extracted ZIP file to {extract_dir}")
      except PermissionError as e:
          print(f"Permission error during extraction: {e}")
      except Exception as e:
          print(f"Failed to extract ZIP file: {e}")
          return

    def handle_tools(self, selected_item, json_dir):
        """Handle and display detailed information for 'tools' category, including extracting ZIP files if necessary.
        
        Parameters:
        selected_item (dict): The selected item data from JSON.
        json_dir (str): The directory where the JSON file was found.
        """
        # Resolve paths relative to the directory where the JSON file is located
        py_path = os.path.dirname(os.path.abspath(__file__)) + "/"
        exe_path = os.path.join(py_path, json_dir, selected_item.get("exePath", ""))
        exe_path = os.path.normpath(exe_path)
        zip_path = os.path.join(py_path, json_dir, selected_item.get("ZIPPath", ""))
        zip_path = os.path.normpath(zip_path)
        
        # Check if the executable path exists
        if os.path.exists(exe_path):
            self.run_exe(exe_path)
        elif os.path.exists(zip_path):
            self.un_zip(zip_path)
            self.run_exe(exe_path)
        else:
            print(self.locale_handler.locale_texts["file_not_found"])
            print("\n downloadUrl: " + selected_item["downloadUrl"])

    def print_detailed_info(self, item):
        """Print detailed information of the selected item, showing each key-value pair."""
        print("\nDetails for selected item:\n")
        for key, value in item.items():
            print(f" {key}: {value}")
        print("\n")

    def handle_user_selection(self, results):
        """Handle the user's selection from the displayed results and print detailed information."""
        locale_texts = self.locale_handler.locale_texts
        choice = input(locale_texts["enter_choice"])
        try:
            choice = int(choice)
        except ValueError:
            print(locale_texts["invalid_input"])
            return

        if choice == 0:
            return

        if 1 <= choice <= len(results):
            selected_category, selected_item = results[choice - 1]
            json_dir = os.path.dirname(selected_item.get("sourceFile", ""))  # Assuming `sourceFile` is where the JSON file is located

            # Print detailed information of the selected item
            self.print_detailed_info(selected_item)
            
            # Delegate the handling based on category
            if selected_category in ["github", "website"]:
                self.handle_github_or_website(selected_item)
            elif selected_category == "tools":
                self.handle_tools(selected_item, json_dir)
        else:
            print(locale_texts["invalid_selection"])

    def main(self):
        """Main function to run the JSON Bookmark Tool."""
        json_data = self.load_json_data("./resources")
        arguments = ' '.join(sys.argv[1:])
        
        while True:
            if arguments != "":
                input_command = arguments
                arguments = ""
            else:
                input_command = input("\n" + self.locale_handler.locale_texts["input_tips"]).strip()
            command, keyword, category = self.parse_arguments(input_command)
            
            if command is None: continue

            results = self.execute_command(command, keyword, category, json_data)
            
            if not results: continue

            self.display_results(results)
            self.handle_user_selection(results)

if __name__ == "__main__":
    locale_handler = LocaleHandler()
    string_formatter = StringFormatter()
    app = JsonBookmarkTool(locale_handler, string_formatter)
    app.main()
