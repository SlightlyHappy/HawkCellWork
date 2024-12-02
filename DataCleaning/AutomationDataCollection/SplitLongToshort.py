def split_text_into_chunks(text, num_chunks=3):
    # Calculate the length of each chunk
    chunk_size = len(text) // num_chunks
    chunks = []

    # Split the text into chunks
    for i in range(num_chunks):
        start_index = i * chunk_size
        if i == num_chunks - 1:  # Last chunk takes the remainder of the text
            end_index = len(text)
        else:
            end_index = (i + 1) * chunk_size
        chunks.append(text[start_index:end_index])

    return chunks

def main(input_data):
    input_text = input_data.get('text', '')
    if not input_text:
        return {'chunk_1': '', 'chunk_2': '', 'chunk_3': ''}
    
    chunks = split_text_into_chunks(input_text)
    return {f'chunk_{i + 1}': chunk for i, chunk in enumerate(chunks)}

# Example usage in Zapier
if __name__ == "__main__":
    input_data = {
        'text': 'Your long scraped HTML text goes here...'
    }
    result = main(input_data)
    print(result)