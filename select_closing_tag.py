import sublime, sublime_plugin, re
from .utils import get_end_index, get_start_index, re_tag


class SelectClosingHtmlCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selections = self.view.sel()

        file_content = self.view.substr(sublime.Region(0, self.view.size()))

        for selection in selections:
            a, b = sorted(selection.to_tuple())
            if file_content[a - 1] == "<" and file_content[b] in " >":
                # Select closing tag
                end_index = get_end_index(file_content, a - 1)
                if end_index is None or file_content[end_index - 1] != ">":
                    continue

                start_index = file_content[: end_index - 1].rindex("</")
                self.view.sel().add(sublime.Region(start_index + 2, end_index - 1))

            elif file_content[a - 2 : a] == "</" and file_content[b] in " >":
                # Select opening tag
                print("select opening")

                start_index = get_start_index(file_content, b + 1)
                size = len(re.match(re_tag, file_content[start_index:b]).group(2))
                self.view.sel().add(
                    sublime.Region(start_index + 1, start_index + size + 1),
                )
