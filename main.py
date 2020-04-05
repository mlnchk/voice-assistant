import audio
import gui

def main(GUI = True):
    if GUI:
        core = gui.AppCore()
        core.MainLoop()
    else:
        audio.main_cli()

if __name__ == "__main__":
    main(True)