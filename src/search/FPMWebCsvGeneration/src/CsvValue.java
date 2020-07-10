import java.util.List;
import java.util.Map;

public class CsvValue {

	private String word;

	private Integer noOfDocumentsContainingThisWord;

	// Key = documentId, value = total occurrence of word in the document
	private Map<Integer, Integer> documentId;

	private List<String> documentName;
	
	// Key = documentId, value = word positions in the document
	private List<WordPositions> wordPositions;

	public String getWord() {
		return word;
	}

	public void setWord(String word) {
		this.word = word;
	}

	public List<String> getDocumentName() {
		return documentName;
	}

	public void setDocumentName(List<String> documentName) {
		this.documentName = documentName;
	}

	public CsvValue() {
	}

	public Integer getNoOfDocumentsContainingThisWord() {
		return noOfDocumentsContainingThisWord;
	}

	public void setNoOfDocumentsContainingThisWord(
			Integer noOfDocumentsContainingThisWord) {
		this.noOfDocumentsContainingThisWord = noOfDocumentsContainingThisWord;
	}

	public List<WordPositions> getWordPositions() {
		return wordPositions;
	}

	public void setWordPositions(List<WordPositions> wordPositions) {
		this.wordPositions = wordPositions;
	}

	public Map<Integer, Integer> getDocumentId() {
		return documentId;
	}

	public void setDocumentId(Map<Integer, Integer> documentId) {
		this.documentId = documentId;
	}

}
