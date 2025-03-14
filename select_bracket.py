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


# a = ({1: [(1 * 2) % 5 + 1] * 3})
# a = (1 + 1)


def _select_matching(view, selection):
    if abs(selection.a - selection.b) == 1:
        c = view.substr(selection)
        cursor = min(selection.to_tuple()) if c in "({[" else max(selection.to_tuple())
    else:
        cursor = max(selection.to_tuple())
    selection = sublime.Region(cursor, cursor)
    view.sel().add(selection)
    view.run_command("move_to", args={"to": "brackets"})
    new_cursor = view.sel()[0].a
    view.sel().subtract(view.sel()[0])

    if set(selection.to_tuple()) != {new_cursor}:
        # By default, sublime try to jump outside
        if new_cursor > cursor:
            to_check = view.substr(sublime.Region(cursor, cursor + 1))
        else:
            to_check = view.substr(sublime.Region(cursor - 1, cursor))

        jump_inside = not re.match(re_bracket, to_check)
        if (new_cursor > cursor) ^ jump_inside:
            return sublime.Region(new_cursor - 1, new_cursor)
        return sublime.Region(new_cursor, new_cursor + 1)

    # The command fail, fallback on search
    # TODO: will match brackets inside strings :/
    print("Fallback")
    res = view.find(re_bracket, selection.end())
    return selection if res.to_tuple() == (-1, -1) else res
