import sublime, sublime_plugin, re
from .utils import get_end_index, get_start_index, re_tag, re_closing_tag


class SelectClosingHtmlCommand(sublime_plugin.TextCommand):
    def run(self, edit, keep_selection=False):
        selections = self.view.sel()

        file_content = self.view.substr(sublime.Region(0, self.view.size()))

        for selection in list(selections):
            a, b = sorted(selection.to_tuple())
            if file_content[a - 1] == "<" and file_content[b] in " >":
                # Select closing tag
                end_index = get_end_index(file_content, a - 1)
                if end_index is None or file_content[end_index - 1] != ">":
                    continue

                start_index = file_content[: end_index - 1].rindex("</")
                self.view.sel().add(sublime.Region(start_index + 2, end_index - 1))

                if not keep_selection:
                    self.view.sel().subtract(selection)

            elif file_content[a - 2 : a] == "</" and file_content[b] in " >":
                # Select opening tag
                start_index = get_start_index(file_content, b + 1)
                size = len(
                    re.match(
                        re_tag, file_content[start_index:b], re.IGNORECASE | re.DOTALL
                    ).group(2)
                )
                self.view.sel().add(
                    sublime.Region(start_index + 1, start_index + size + 1),
                )

                if not keep_selection:
                    self.view.sel().subtract(selection)
            else:
                # Select the parent tag
                idx = self.view.find("<", selection.begin(), sublime.REVERSE).a
                if (
                    idx >= 0
                    and self.view.find(">", selection.begin(), sublime.REVERSE).a
                ):
                    # If we are inside a closing tag, we want to select it
                    if re.fullmatch(
                        re_closing_tag[:-1],
                        self.view.substr(sublime.Region(idx, b)),
                        re.IGNORECASE | re.DOTALL,
                    ):
                        b = idx
                end_index = get_end_index(file_content, b, stop_at_close_error=True)
                if end_index is None or file_content[end_index - 1] != ">":
                    continue

                start_index = file_content[: end_index - 1].rindex("</")
                self.view.sel().subtract(selection)
                self.view.sel().add(sublime.Region(start_index + 2, end_index - 1))
