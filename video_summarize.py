from pytube import YouTube
import srt
from moviepy.editor import *
import datetime
import nltk
import heapq
nltk.download('punkt')
nltk.download('stopwords')


# url = input("Input the URL: ")
class VideoSummarize:
    def __init__(self, link):
        self.url = link

    def summarize(self):
        YouTube(self.url).streams.first().download(filename='file')
        source = YouTube(self.url)
        en_caption = source.captions['en']
        caption = (en_caption.generate_srt_captions())

        s = srt.parse(caption)
        subtitles = list(s)

        for subtitle in subtitles:
            subtitle.content = subtitle.content.lower()

        dic = {}
        for subtitle in subtitles:
            dic[subtitle.content.lower()] = [subtitle.start, subtitle.end]

        transcript = ""
        for subtitle in subtitles:
            transcript += subtitle.content + " "

        sentenceList = nltk.sent_tokenize(transcript)
        stopwords = nltk.corpus.stopwords.words('english')

        word_frequencies = {}
        for word in nltk.word_tokenize(transcript):
            if word not in stopwords:
                if word not in word_frequencies.keys():
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1
        maximum_frequncy = max(word_frequencies.values())

        for word in word_frequencies.keys():
            word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)
        sentence_scores = {}

        for sent in sentenceList:
            for word in nltk.word_tokenize(sent.lower()):
                if word in word_frequencies.keys():
                    if len(sent.split(' ')) < 30:
                        if sent not in sentence_scores.keys():
                            sentence_scores[sent] = word_frequencies[word]
                        else:
                            sentence_scores[sent] += word_frequencies[word]

        summary_sentences = heapq.nlargest(15, sentence_scores, key=sentence_scores.get)
        summary = ' '.join(summary_sentences)
        summary = nltk.sent_tokenize(summary)

        subtitle_list = []
        for sentence in summary:
            for subtitle in subtitles:
                r = sentence.find(subtitle.content)
                if r != -1:
                    subtitle_list.append(sentence[r:r+len(subtitle.content)])

        apollo = VideoFileClip("file.mp4")
        clips = []
        prev = datetime.timedelta(0, 0, 0)
        for item in subtitle_list:
            if dic[item][0] < prev and dic[item][1] > prev:
                clips[-1][1] = dic[item][1]
            else:
                clips.append([dic[item][0], dic[item][1]])
            prev = dic[item][1]

        video = concatenate_videoclips([apollo.subclip(str(clip[0]), str(clip[1])) for clip in clips])
        video.write_videofile("summarized.mp4")
