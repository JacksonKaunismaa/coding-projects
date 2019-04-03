package TeachPanel;

import java.awt.event.ActionEvent;
import java.util.EventListener;
import java.util.EventObject;

public interface TeachPanelEventListener extends EventListener {
    void exitedOrFinished();
}

