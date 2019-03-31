//----------------------------------------------------------------------------------------|
//  Question.java - Parsing and reading questions that QuestionPanel.java interprets as   |
//  questions to test the user on, understands the markup language using regex.           |
//----------------------------------------------------------------------------------------|
//  Author: Jackson Kaunismaa                                                             |
//  Date: 2019-01-15                                                                      |
//----------------------------------------------------------------------------------------|
//  Input: File text formatted like a markup language                                     |
//  Output: Question that the user can be asked, and vectors/animations for the grid      |
//----------------------------------------------------------------------------------------|
package QuestionPanel;

import MathBase.Vector2D;
import TeachPanel.TeachInfo;

import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Question extends TeachInfo {

    private QuestionReader questionReader;
    private ArrayList<RandomContainer> answer;
    private String questionDisplay, questionType, foundAnswerDisplay;
    private Matcher typeGetter, ansDisplayMatcher, scoreMatcher, alternateAnswerMatcher;
    private Pattern randomPattern;
    private Integer foundScore;

    public Question(String lineInfo) {
        super(lineInfo);
        typeGetter = Pattern.compile("<type=(.+?)>").matcher(lineInfo);
        ansDisplayMatcher = Pattern.compile("<reveal>(.+?)</reveal>").matcher(lineInfo);
        scoreMatcher = Pattern.compile("<score=(\\d+?)/\\d+?>").matcher(lineInfo);
        randomPattern = Pattern.compile("R\\((.+?),(.+?),(\\d+)\\)");
        alternateAnswerMatcher = Pattern.compile("<answer>(.+?)</answer>").matcher(lineInfo);

        questionDisplay = null;
        answer = null;
        questionType = null;
        foundAnswerDisplay = null;
        foundScore = null;
    }

    private String getRandomByID(int ID) {
        for (RandomContainer ans : answer) {
            if (ans.getID() == ID)
                return ans.toString();
        }
        return "ANSWER NOT FOUND";
    }

    public String getQuestionDisplay() {
        formatQuestion();
        return questionDisplay;
    }

    String formatQuestion() {
        if (questionDisplay == null) {
            questionDisplay = "";
            if (answer == null)
                answer = new ArrayList<>();
            String currentText = findDisplayInfo();
            Matcher randomMatcher = randomPattern.matcher(currentText);
            while (randomMatcher.find()) {
                answer.add(new RandomContainer(
                        Double.parseDouble(randomMatcher.group(1)),
                        Double.parseDouble(randomMatcher.group(2)),
                        Integer.parseInt(randomMatcher.group(3))));
            }

            StringBuffer resultString = new StringBuffer();
            Matcher replMatcher = Pattern.compile("R\\(.+?,.+?,(\\d+)\\)").matcher(currentText);
            while (replMatcher.find()) {
                String repl = getRandomByID(Integer.parseInt(replMatcher.group(1)));
                replMatcher.appendReplacement(resultString, repl);
            }
            replMatcher.appendTail(resultString);
            questionDisplay = resultString.toString();
        }
        return questionDisplay;
    }

    public String getType() {
        if (questionType == null) {
            if (typeGetter.find()) {
                questionType = typeGetter.group(1);
            }
        }
        return questionType;
    }

    @Override
    public ArrayList<Vector2D> getVectorInfo() {
        try {
            super.getVectorInfo();
        } catch (NumberFormatException ignored) {
            foundVector = new ArrayList<>();
            if (answer == null)
                answer = new ArrayList<>();
            Matcher vectorMatcher = Pattern.compile("<vector>(.+?)</vector>").matcher(lineInfo);
            if (vectorMatcher.find()) {
                String vectorText = vectorMatcher.group(1);
                StringBuffer resultString = new StringBuffer();
                Matcher replMatcher = Pattern.compile("R\\((.+?),(.+?),\\d+\\)").matcher(vectorText);
                while (replMatcher.find()) {
                    RandomContainer repl = new RandomContainer(replMatcher.group(1), replMatcher.group(2), 0);
                    replMatcher.appendReplacement(resultString, repl.toString());
                }
                replMatcher.appendTail(resultString);
                String vectorString;
                vectorString = resultString.toString();
                findVectorInfo(vectorString);
            }
        }
        if (answer != null && answer.size() == 0)
            for (Vector2D vec : foundVector) {
                answer.add(new RandomContainer(vec.getVectorX()));
                answer.add(new RandomContainer(vec.getVectorY()));
            }
        return foundVector;
    }

    private void altAnswer() {
        if (alternateAnswerMatcher.find()) {
            answer.clear();
            Matcher numMatcher = Pattern.compile("([^,]+)").matcher(alternateAnswerMatcher.group(1));
            while (numMatcher.find()) {
                answer.add(new RandomContainer(Double.parseDouble(numMatcher.group(1))));
            }
        }
    }

    public boolean checkAnswer(ArrayList<Double> guess) {
        altAnswer();
        if (guess.size() != getAnswerSize()) return false;
        for (int i = 0; i < answer.size(); i++) {
            if (!answer.get(i).close(guess.get(i))) return false;
        }
        return true;
    }

    private ArrayList<String> truncateDoubleArray(ArrayList<Double> doubleArrayList) {
        ArrayList<String> res = new ArrayList<>();
        for (Double doub : doubleArrayList) {
            res.add(String.format("%.1f", doub));
        }
        return res;
    }

    private ArrayList<String> truncateRandomContainerArray(ArrayList<RandomContainer> rcList) {
        ArrayList<Double> doubleArrayList = new ArrayList<>();
        for (RandomContainer rc : rcList)
            doubleArrayList.add(rc.getValue());
        return truncateDoubleArray(doubleArrayList);
    }

    public String getAnswerDisplay(ArrayList<Double> guess) {
        if (foundAnswerDisplay == null) {
            if (ansDisplayMatcher.find()) {
                foundAnswerDisplay = ansDisplayMatcher.group(1);
                foundAnswerDisplay = "Your guess: " + truncateDoubleArray(guess) + " <br> Actual answer: " + truncateRandomContainerArray(answer) + "<br>" + foundAnswerDisplay;
            } else {
                System.out.println("No text found!");
                return "-=-=-=-=-=-=";
            }
        }
        return "<html>" + foundAnswerDisplay + "</html>";

    }

    public int getScore() {
        if (foundScore == null) {
            foundScore = 0;
            if (scoreMatcher.find()) {
                foundScore = Integer.parseInt(scoreMatcher.group(1));
            }
        }
        return foundScore;
    }

    public int getAnswerSize() {
        return answer.size();
    }
}
