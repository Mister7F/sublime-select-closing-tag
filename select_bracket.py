import sublime, sublime_plugin, re


class CustomExpandSelectionBracketCommand(sublime_plugin.TextCommand):
    """Select the next bracket, and keep the current selection."""

    def run(self, edit, keep_selection=False):
        selections = list(self.view.sel())

        for selection in selections:
            self.view.sel().subtract(selection)

        to_select = [
            (selection, _select_matching(self.view, selection))
            for selection in selections
        ]

        if not keep_selection:
            to_select_dict = {
                tuple(sorted(a.to_tuple())): tuple(sorted(b.to_tuple()))
                for a, b in to_select
            }
            # In case both brackets are already selected, and `keep_selection == False`,
            # then we want to keep only one bracket selected
            for selection, new_selection in to_select_dict.items():
                if new_selection in to_select_dict:
                    to_remove = max(selection, new_selection)
                    to_select = [
                        (a, b) for a, b in to_select if b.to_tuple() != to_remove
                    ]

        for _, selection in to_select:
            self.view.sel().add(selection)

        if keep_selection:
            for selection in selections:
                if selection.a != selection.b:
                    self.view.sel().add(selection)


re_bracket = r"[\(\)\{\}\[\]]"


def _select_matching(view, selection):
    view.sel().add(selection)
    view.run_command("move_to", args={"to": "brackets"})
    new_selection = view.sel()[0]
    view.sel().subtract(selection)
    view.sel().subtract(new_selection)

    if len(set(selection.to_tuple()) & set(new_selection.to_tuple())) == 4:
        b = max(selection.to_tuple())
        c = view.substr(sublime.Region(b, b + 1))
        d = view.substr(sublime.Region(b - 1, b))
        if re.match(re_bracket, c) and not re.match(re_bracket, d):
            return sublime.Region(new_selection.a - 1, new_selection.b)
        return sublime.Region(new_selection.a, new_selection.b + 1)

    # The command fail, fallback on search
    # TODO: will match brackets inside strings :/
    print("Fallback")
    res = view.find(re_bracket, selection.end())
    return selection if res.to_tuple() == (-1, -1) else res
