from dataclasses import dataclass, field
import re
from re import Pattern
from typing import List, Literal, Mapping, Optional, Set, Tuple, TypeAlias, TypedDict, Union, cast, Callable, Tuple
from os import PathLike
from enum import Enum

'''
Repetição é melhor que acoplamento desnecessário, mantenha as funções
separadas com responsabilidade única (S de Solid), ex.: Uma função pra
android e outra pra iphone é melhor que uma função reaproveitada para
os dois dispositivos, agora pode ser muito parecido o processo, mas no
futuro pode ser que android e iphone mudem muito a estrutura no app do
whatsapp.

DRY (Não Repita Código) é um princípio importante, mas sempre mantenha
o princípio de responsabilidade única (S de SOLID) antes do DRY, para
facilitar desenvolvimento futuro. Não combine as funções de extração
para android e iphone
'''

OptionalStrOrFalse: TypeAlias = Optional[Union[Literal[False], str]]
TMessageData: TypeAlias = Union['MessageData', Mapping[Literal["ERRO"], str]]
FileLike: TypeAlias = Union[str, bytes, PathLike]
RePattern: TypeAlias = str | Pattern[str]
ExtractTwoGroups: TypeAlias = Callable[[RePattern, str], Tuple[str, str]]

@dataclass(unsafe_hash=True)
class MessageData(TypedDict):
    Name: str
    ID: int
    Date: str
    Time: str
    Message: str
    FileAttached: OptionalStrOrFalse
    @property
    def is_valid(self):
        return all((self.sender, self.sender_id, self.date, self.time, self.message))

@dataclass
class MessagesStore:
    messages: List[MessageData] = field(default_factory=list)
    def __iadd__(self, message_data: MessageData):
        if message_data.is_valid:
            self.messages.append(message_data)
        return self

@dataclass
class UniqueIdsStore:
    unique_ids: Mapping[str, int] = field(default_factory=dict)
    def __iadd__(self, sender: str):
        if sender not in self.unique_ids:
            self.unique_ids[sender] = len(self.unique_ids) + 1
        # else
        return self

def remove_ext(file: str) -> Tuple[str, str]:
    ''' Ex.: Imagem.seila.jpg -> (Imagem.seila, .jpg) '''
    file_parts = file.split('.')
    filename_no_ext = '.'.join(file_parts[:len(file_parts)-1:])
    ext = f'.{file_parts[-1::]}'
    return (filename_no_ext, ext)

@dataclass
class NameCounter:
    pattern: RePattern
    unique_names: Set[str] = field(default_factory=set)
    unsupported_groupchat_err = [{'ERRO': "Conversas em grupo não suportadas"}]
    def add(self, name: str):
        self.unique_names.add(name)
    @property
    def is_groupchat(self) -> bool:
        '''
        @todo Não é um método preciso:
          - Um grupo com 2 pessoas não iria ser considerado grupo;
          - Pessoas diferentes com mesmo nome de contato.
        '''
        return len(self.unique_names) > 2
        
class FileParsingMethod(Enum):
    NO_FILE = 0
    MEDIA = 1
    PDF = 2
    OFFICE = 3
    OTHER = 4
    
def parse_filetype(filename: Optional[str]) -> FileParsingMethod:
    if not filename:
        return FileParsingMethod.NO_FILE
    # else
    extensions_map = {
        FileParsingMethod.OFFICE: ('.docx', '.docm', '.doc', 'odt', '.pptx', '.ppt', 'odp', '.xlsx', 'xls', 'ods'),
        FileParsingMethod.MEDIA: ('.jpg', '.jpeg', '.opus', '.mp4'),
        FileParsingMethod.PDF: ('.pdf',)
    }
    for filetype, extensions in extensions_map.items():
        if filename.endswith(extensions):
            return filetype
    # else
    return FileParsingMethod.OTHER

def extract_first_second_group(regex: RePattern, line:str):
    match = re.search(regex, line)
    if not match:
        return (None, None)
    # else
    group1 = cast(str, match.group(1)) or None
    group2 = cast(str, match.group(2)) or None
    return (group1, group2)

extract_datetime: ExtractTwoGroups = lambda regex, line: extract_first_second_group(regex, line)
extract_sender_message: ExtractTwoGroups = lambda regex, line: extract_first_second_group(regex, line)


date_time_pattern = re.compile(r'\[(\d{2}/\d{2}/\d{2,4}), (\d{2}:\d{2}:\d{2})\]')
message_pattern = re.compile(r'\] (.*?): (.*)')

def extract_info_iphone(input_file: FileLike, attachment_files: Tuple[str]) -> TMessageData:
    messageStore = MessagesStore()
    nameCounter = NameCounter(message_pattern)
    uniqueIds = UniqueIdsStore()

    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        sender: str = None
        sender_id: int = None
        date: str = None
        time: str = None
        message: str = None
        file_attached: OptionalStrOrFalse = None
        well_formated = lambda: all((sender, sender_id,  date, time, message))

        date, time = extract_datetime(date_time_pattern, line)
        sender, message = extract_sender_message(message_pattern, line)
        nameCounter.add(sender)
        if nameCounter.is_groupchat:
            return nameCounter.unsupported_groupchat_err
 
        if not (sender or message):
            continue
        
        file_attached = False

        uniqueIds += sender
        sender_id = uniqueIds.unique_ids[sender]

        if any(ext in message for ext in ['.jpg']):
            file_pattern = r'(\S+)\.(jpg)'
            file_match = re.search(file_pattern, message)
            if file_match:
                file_attached = file_match.group()

        # if any(ext in message for ext in ['.docx', '.jpg']):
        #     file_pattern = r'(\S+)\.(docx|jpg)'
        #     file_match = re.search(file_pattern, message)
        #     if file_match:
        #         if file_match.group(2) == 'docx':
        #             file_attached = file_match.group(1) + '.pdf'  # Only filename for DOCX
        #         else:
        #             file_attached = file_match.group()  # Full filename with extension for others
        if '.docx' in message:
            file_pattern = r'<anexado:\s*(.+?)\.docx>'
            file_match = re.search(file_pattern, message)
            if file_match:
                file_attached = file_match.group(1) + '.pdf'  # Full filename with .pdf extension
            else:
                file_attached = None  # or handle the case when no match is found

        elif any(ext in message for ext in ['.opus']):
            file_pattern = r'(\S+)\.(opus)'
            file_match = re.search(file_pattern, message)
            file_attached = file_match.group()

        elif any(ext in message for ext in ['.mp4']):
            file_pattern = r'(\S+)\.(mp4)'
            file_match = re.search(file_pattern, message)
            file_attached = file_match.group()

        elif '.pdf' in message:
            file_pattern_pdf = r'<anexado:\s*(.*?\.pdf)>'
            # file_pattern_pdf = r'<anexado:\s*(.*?\.pdf)>'
            file_pattern_pdf_match = re.search(file_pattern_pdf, message)
            #print(file_pattern_pdf_match)
            if file_pattern_pdf_match:
                print("result")
                print("-----------------------------")
                file_attached = file_pattern_pdf_match.group(1)
                #print(file_attached)

        # Apenas vai adicionar no contraint messageStore.is_valid
        messageStore += (
            MessageData(**{
                'Name': sender,
                'ID': sender_id,
                'Date': date,
                'Time': time,
                'Message': message,
                'FileAttached': file_attached
            })
        )

    return messageStore.messages



date_time_pattern = re.compile(r'(\d{2}/\d{2}/\d{2,4}),{0,1} (\d{2}:\d{2}) -')
message_pattern = re.compile(r'- (.*?): (.*)')
# Pode ser em qualquer língua, (file attached), (arquivo anexado), etc
attachment_pattern = re.compile(r'(?<=\..{3} )\(.{3,25}?\)|(?<=\..{4} )\(.{3,25}?\)')

def extract_info_android(input_file: FileLike, attachment_files: Tuple[str]) -> TMessageData:
    messageStore = MessagesStore()
    nameCounter = NameCounter(message_pattern)
    uniqueIds = UniqueIdsStore()

    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        sender: str = None
        sender_id: int = None
        date: str = None
        time: str = None
        message: str = None
        file_attached: OptionalStrOrFalse = None

        date, time = extract_datetime(date_time_pattern, line)
        sender, message = extract_sender_message(message_pattern, line)
        nameCounter.add(sender)
        if nameCounter.is_groupchat:
            return nameCounter.unsupported_groupchat_err
 
        if not (sender or message):
            continue

        file_attached = False

        uniqueIds += sender
        sender_id = uniqueIds.unique_ids[sender]
            
        attachment_test = re.split(attachment_pattern, message)
        if len(attachment_test):
            attachment_test[0] = attachment_test[0].strip()
        has_attachment = len(attachment_test) == 2 and attachment_test[0] in attachment_files
        attached_filename:str = None
        if has_attachment:
            attached_filename = attachment_test[0]
            message = ' (Arquivo Anexado) '.join(attachment_test)
            
        # print(f"attachment_test={attachment_test} attachment_files={attachment_files} has_attachment={has_attachment} attached_filename={attached_filename}")
        filetype = parse_filetype(attached_filename)

        if filetype == FileParsingMethod.MEDIA:
            file_attached = attached_filename            
        elif filetype == FileParsingMethod.OFFICE:
            (file_attached, _) = remove_ext(attached_filename)
            file_attached += '.pdf'
        elif filetype == FileParsingMethod.PDF:
            file_attached = attached_filename

        # Apenas vai adicionar no contraint messageStore.is_valid
        messageStore += (
            MessageData(**{
                'Name': sender,
                'ID': sender_id,
                'Date': date,
                'Time': time,
                'Message': message,
                'FileAttached': file_attached
            })
        )

    return messageStore.messages



    # if len(unique_names) > 2:
    #     # Limpa a lista de entradas anteriores
    #     extracted_info.clear()
    #     # Adiciona a nova entrada no início da lista
    #     extracted_info.insert(0, {'ERRO': "Conversas em grupo não suportadas"})
    #     # Levanta um erro
    #     #raise ValueError("Conversas em grupo não suportadas")
    #     # print(extracted_info)
    #     return messageStore.messages
    # else:
    #     messageStore += ({'Name': sender, 'ID': sender_id, 'Date': date, 'Time': time, 'Message': message, 'FileAttached': file_attached})
    #     return messageStore.messages