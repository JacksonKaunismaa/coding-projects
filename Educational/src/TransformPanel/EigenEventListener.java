package TransformPanel;

import java.util.EventListener;

public interface EigenEventListener extends EventListener {
    void sendEigen(TransformEvent evt);
}
