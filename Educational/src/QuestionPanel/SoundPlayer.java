//----------------------------------------------------------------------------------------|
//  SoundPlayer.java - Given a sound file, plays the sound                                |
//----------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                             |
//  Date: 2019-01-15                                                                      |
//----------------------------------------------------------------------------------------|
//  Input: Sound file string                                                              |
//  Output: Sound                                                                         |
//----------------------------------------------------------------------------------------|
package QuestionPanel;
import javax.sound.sampled.*;
import java.io.File;
import java.io.IOException;
import java.nio.file.FileSystems;

class SoundPlayer {
    void playSound(String soundFile) throws IOException, UnsupportedAudioFileException, LineUnavailableException {
        File f = new File(FileSystems.getDefault().getPath("Sounds", soundFile).toAbsolutePath().toString());  // load file
        AudioInputStream audioIn = AudioSystem.getAudioInputStream(f.toURI().toURL());     // turn file into audio
        Clip clip = AudioSystem.getClip();         // turn audio into playable clip
        clip.open(audioIn);   // open and play clip
        clip.start();
    }

}