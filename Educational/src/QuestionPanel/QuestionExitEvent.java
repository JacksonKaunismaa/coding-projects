//----------------------------------------------------------------------------------------|
//  QuestionExitEvent.java - When the user is done doing  a test, this event is fired so  |
//  that when they return to the test select screen, if they got every question correct,  |
//  it unlocks the next  test for them to complete                                        |
//----------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                             |
//  Date: 2019-01-15                                                                      |
//----------------------------------------------------------------------------------------|
//  Input: boolean as to whether or not a perfect score was obtained on a test            |
//----------------------------------------------------------------------------------------|
package QuestionPanel;

import java.util.EventObject;


public class QuestionExitEvent extends EventObject {
    private boolean completed;

    public QuestionExitEvent(Object source, boolean completed) {
        super(source);
        this.completed = completed;
    }

    public boolean testCompleted() {
        return completed;
    }

}

