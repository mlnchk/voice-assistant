import audio
import gui

GUI = True
CLI = False

def main(mode = True):
    if mode == GUI:
        core = gui.AppCore()
        core.MainLoop()
    else:
        audio.main_cli()

if __name__ == "__main__":
    main(GUI)