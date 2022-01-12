

import baopig as bp


if __name__ == "__main__":
    app = bp.Application()
    main = bp.Scene(app)
    dialog1 = bp.Dialog(main, "DialogTest1", ("No", "Maybe", "Yes"), "There is a description")
    bp.Button(main, "Open Dialog1", command=lambda: print("ANSWER :", dialog1.ask()), pos=(10, 10))
    dialog2 = bp.Dialog(main, "DialogTest2", ("No", "Maybe", "Yes"),
                        "There\n is\n another\n great\n and\n awesome\n description",
                        frame_style={"size": (500, 200)}, index_default_choice=2)
    bp.Button(main, "Open Dialog2", command=lambda: print("ANSWER :", dialog2.ask()), pos=(120, 120))
    app.launch()


