//----------------------------------------------------------------------------------------|
//  QuestionReader.java - Parsing and reading questions that QuestionPanel.java interprets|
//  as questions to test the user on, understands the markup language using regex.        |
//----------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                             |
//  Date: 2019-01-15                                                                      |
//----------------------------------------------------------------------------------------|
//  Input: File text formatted like a markup language                                     |
//  Output: Question that the user can be asked, and vectors/animations for the grid      |
//----------------------------------------------------------------------------------------|
package QuestionPanel;

import TeachPanel.TeachReader;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.nio.file.FileSystems;
import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class QuestionReader extends TeachReader {
    private ArrayList<Question> allQuestions;
    private String filename, questionDir;

    public QuestionReader(String questionDir, String filename) throws IOException {
        super(questionDir, filename);
        this.questionDir = questionDir;
        this.filename = filename;
        processTeachInfo();
    }

    public void processTeachInfo() {
        allQuestions = new ArrayList<>();
        headerInfo = null;
        for (String t : strTeachInfo) {   // for each line
            if (headerInfo == null)
                headerInfo = t;   // set aside the first line as the header for the whole thing
            else {
                Question q = new Question(t);
                allQuestions.add(q);
            }
        }
    }

    @Override
    public Question getNext() {
        if (iter + 1 < allQuestions.size())
            iter += 1;
        return allQuestions.get(iter);
    }


    public void resave(int newScore) {
        try {
            Matcher prevScore = Pattern.compile("<score=(\\d+?)/\\d+?>").matcher(headerInfo);
            PrintWriter writer = new PrintWriter(FileSystems.getDefault().getPath(questionDir, filename).toAbsolutePath().toString(), "UTF-8");
            if (prevScore.find()) {
                if (Integer.parseInt(prevScore.group(1)) < newScore)
                    headerInfo = headerInfo.replaceAll("<score=\\d+?/\\d+?>", "<score=" + newScore + "/" + getLength() + ">");
            } else {
                headerInfo += "<score=" + newScore + "/" + getLength() + ">";
            }
            writer.println(headerInfo);
            for (int i = 1; i < strTeachInfo.size(); i++) {
                writer.println(strTeachInfo.get(i));
            }
            writer.close();
        } catch (FileNotFoundException | UnsupportedEncodingException e) {
            e.printStackTrace();
        }
    }
}
