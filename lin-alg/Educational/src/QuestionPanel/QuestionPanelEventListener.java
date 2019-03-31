//----------------------------------------------------------------------------------------|
//  QuestionPanelEventListener.java -  Boiler plate code for adding a new type of event   |
//  listener so the test/question can interact with the test/question selection menu      |
//----------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                             |
//  Date: 2019-01-15                                                                      |
//----------------------------------------------------------------------------------------|

package QuestionPanel;

import java.util.EventListener;

public interface QuestionPanelEventListener extends EventListener {
    void exitUpdate(QuestionExitEvent evt);
}
