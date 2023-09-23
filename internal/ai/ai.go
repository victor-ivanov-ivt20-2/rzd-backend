package ai

import (
	"os"
	"os/exec"
)

func ExecAI(dir string, python string, main string, mp4 string) error {

	err := os.Chdir(dir)
	if err != nil {
		return err
	}

	cmd := exec.Command(python, main, mp4)
	err = cmd.Run()
	if err != nil {
		return err
	}
	return nil

}
