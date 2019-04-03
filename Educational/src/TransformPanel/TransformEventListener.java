package TransformPanel;

import java.util.EventListener;

public interface TransformEventListener extends EventListener {
    void applyTransform(TransformEvent evt);
}
