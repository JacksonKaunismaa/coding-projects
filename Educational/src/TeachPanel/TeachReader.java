//----------------------------------------------------------------------------------------|
//  TeachReader.java - Parsing and reading questions that TeachPanel.java interprets      |
//  as questions to test the user on, understands the markup language using regex.        |
//----------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                             |
//  Date: 2019-01-15                                                                      |
//----------------------------------------------------------------------------------------|
//  Input: File text formatted like a markup language                                     |
//  Output: Question that the user can be asked, and vectors/animations for the grid      |
//----------------------------------------------------------------------------------------|
package TeachPanel;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class TeachReader {
    protected List<String> strTeachInfo;
    private ArrayList<TeachInfo> allTeachInfo;
    protected String headerInfo;
    protected int iter;
    private Path path;

    public TeachReader(String questionDir, String filename) throws IOException {
        path = FileSystems.getDefault().getPath(questionDir, filename).toAbsolutePath();
        allTeachInfo = new ArrayList<>();
        headerInfo = null;
        iter = -1;
        readTeachInfo();
        processTeachInfo();
    }

    private List<String> readTeachInfo() throws IOException {
        strTeachInfo = Files.readAllLines(path, StandardCharsets.UTF_8);
        return strTeachInfo;
    }

    public void processTeachInfo() {
        for (String t : strTeachInfo) {
            if (headerInfo == null)
                headerInfo = t;   // set aside the first line as the header for the whole thing
            else {
                TeachInfo teachInfo = new TeachInfo(t);
                allTeachInfo.add(teachInfo);
            }
        }
    }


    public TeachInfo getNext() {
        if (iter + 1 < allTeachInfo.size())
            iter += 1;
        return allTeachInfo.get(iter);
    }

    TeachInfo getPrevious() {
        if (iter >= 1)
            iter -= 1;
        return allTeachInfo.get(iter);
    }

    public int getIter() {
        return iter;
    }

    public int getLength() {
        return strTeachInfo.size() - 1;
    }

    public String getHeaderInfo() {
        return headerInfo;
    }
}
