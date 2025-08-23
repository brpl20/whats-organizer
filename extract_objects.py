from dataclasses import dataclass, field
import re
from re import Pattern
from typing import Iterator, List, Literal, Mapping, Optional, Set, Tuple, TypeAlias, TypedDict, Union, cast, Callable, Tuple
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

StrOrFalse: TypeAlias = Union[Literal[False], str]
TMessageData: TypeAlias = Union['MessageData', Mapping[Literal["ERRO"], str]]
FileLike: TypeAlias = Union[str, bytes, PathLike]
RePattern: TypeAlias = str | Pattern[str]
ExtractTwoGroups: TypeAlias = Callable[[RePattern, str], Tuple[str, str]]


class MessageData(TypedDict):
    Name: str
    ID: int
    Date: str
    Time: str
    Message: str
    FileAttached: StrOrFalse
    IsApple: bool


@dataclass
class MessagesStore:
    messages: List[MessageData] = field(
        init=False,
        default_factory=list
    )
    required_fields: tuple = field(
        init=False,
        default=(
            'Name',
            'ID',
            'Date',
            'Time',
            'Message'
        )
    )

    def __iadd__(self, messageData: MessageData):
        if not all(tuple(messageData.get(field, None) for field in self.required_fields)):
            return self

        self.messages.append(messageData)
        return self


@dataclass
class UniqueIdsStore:
    unique_ids: Mapping[str, int] = field(init=False, default_factory=dict)
    unsupported_groupchat_err: List[Mapping[Literal["ERRO"], str]] = field(
        init=False,
        default_factory=lambda: [{'ERRO': "Conversas em grupo não suportadas"}]
    )

    def __iadd__(self, sender: str):
        if sender not in self.unique_ids:
            self.unique_ids[sender] = len(self.unique_ids) + 1
        # else
        return self

    @property
    def is_groupchat(self) -> bool:
        '''
        @todo Não é um método preciso:
          - Um grupo com 2 pessoas não iria ser considerado grupo;
          - Pessoas diferentes com mesmo nome de contato.
        '''
        return len(self.unique_ids) > 2


def remove_ext(file: str) -> Tuple[str, str]:
    ''' Ex.: Imagem.seila.jpg -> (Imagem.seila, .jpg) '''
    file_parts = file.split('.')
    filename_no_ext = '.'.join(file_parts[:len(file_parts)-1:])
    ext = f'.{file_parts[-1::]}'
    return (filename_no_ext, ext)


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
    extensions_map: Mapping[FileParsingMethod, Tuple[str]] = {
        FileParsingMethod.OFFICE: ('.docx', '.docm', '.doc', 'odt', '.pptx', '.ppt', 'odp', '.xlsx', 'xls', 'ods'),
        FileParsingMethod.MEDIA: ('.jpg', '.jpeg', '.opus', '.mp4'),
        FileParsingMethod.PDF: ('.pdf',)
    }
    for filetype, extensions in extensions_map.items():
        if filename.endswith(extensions):
            return filetype
    # else
    return FileParsingMethod.OTHER


def extract_first_second_group(regex: RePattern, line: str):
    match = re.search(regex, line)
    if not match:
        return (None, None)
    # else
    group1 = cast(str, match.group(1)) or None
    group2 = cast(str, match.group(2)) or None
    return (group1, group2)


extract_datetime: ExtractTwoGroups = lambda regex, line: extract_first_second_group(
    regex, line)
extract_sender_message: ExtractTwoGroups = lambda regex, line: extract_first_second_group(
    regex, line)
attached_message: Callable[[str], str] = lambda file: f'Arquivo Anexado: {file}'


datetime_pattern_apple = re.compile(
    r'\[([0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4}), ([0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2})\]')
message_pattern_apple = re.compile(r'\] (.*?): (.*)')
attachment_pattern_apple = re.compile(
    r'''<.{3,25}:\s # <Anexado: <Attached: etc
    (.{1,255}?\.[A-Za-z0-9]{2,4})> # qualquercoisa.md, qualquercoisa.jpg, etc
    # Um arquivo pode ter até 255 chars no máximo
    ''',
    re.VERBOSE) # <.{3,25}:\s(.{1,255}?\.[A-Za-z0-9]{2,4})>

datetime_pattern_android = re.compile(r'([0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4}),{0,1} ([0-9]{1,2}:[0-9]{1,2}) -')
message_pattern_android = re.compile(r'- (.*?): (.*)')
# Pode ser em qualquer língua, (file attached), (arquivo anexado), etc
# a extensão se limita a 3-4 chars, caso queira algo por ex .md pra fazer
# parsing especial, precisa alterar, é preciso fazer ou | no regex porque
# lookbehind no python não suporta tamanho variável (apenas usando lib
# externa)
attachment_pattern_android = re.compile(
    r'''
    (?<=\.[A-Z,a-z,0-9]{3}) # Verifica se antes da string há .XXX, ex.: .jpg
    \s\(.{3,25}?\)\s? # Frase em qualquer língua entre parenteses ex.: (Arquivo Anexado)
    | # Python não possui lookbehind com tamanho variável, .ext com 3 a 4 dígitos
    (?<=\.[A-Z,a-z,0-9]{4}) # ex.: .jpeg .webm, extensões com 4 dígitos
    \s\(.{3,25}?\)\s? # (Arquivo Anexado), (File attached), etc
    ''',
    re.VERBOSE)



def read_file_lines(filename: FileLike) -> Iterator[str]:
    with open(filename, 'r', errors='ignore') as file:
        lines = file.readlines()

    for line in lines:
        yield line


def extract_info_iphone(input_file: FileLike, attachment_files: Tuple[str]) -> TMessageData:
    messageStore = MessagesStore()
    uniqueIds = UniqueIdsStore()

    for line in read_file_lines(input_file):
        sender: Optional[str] = None
        sender_id: Optional[int] = None
        date: Optional[str] = None
        time: Optional[str] = None
        message: Optional[str] = None
        file_attached: StrOrFalse = False

        date, time = extract_datetime(datetime_pattern_apple, line)
        sender, message = extract_sender_message(message_pattern_apple, line)

        if not (sender or message):
            continue

        uniqueIds += sender
        sender_id = uniqueIds.unique_ids[sender]

        if uniqueIds.is_groupchat:
            return uniqueIds.unsupported_groupchat_err

        matches = re.search(attachment_pattern_apple, message)
        attachment_test = (matches.groups() or ()) if matches else ()
        filename_group = 0
        has_attachment = (
            len(attachment_test) > filename_group and 
            attachment_test[filename_group] in attachment_files
        )
        
        # DEBUG iPhone DOCX
        if 'FORMULÁRIO' in message and 'docx' in message:
            print(f"🔍 DEBUG iPhone DOCX:")
            print(f"  Message: {message}")
            print(f"  attachment_test: {attachment_test}")
            print(f"  attachment_files: {attachment_files}")
            print(f"  has_attachment: {has_attachment}")
            if attachment_test:
                print(f"  Captured filename: {attachment_test[filename_group]}")
                print(f"  Filename in files? {attachment_test[filename_group] in attachment_files}")
        
        if has_attachment:
            file_attached = attachment_test[filename_group] or None
            if file_attached:
                message = attached_message(file_attached)
            
        filetype = parse_filetype(file_attached)

        match filetype:
            # case w if w in (FileParsingMethod.MEDIA, FileParsingMethod.PDF):
            case FileParsingMethod.OFFICE:
                file_attached, _ = remove_ext(file_attached)
                file_attached += '.pdf'


        # Apenas vai adicionar no caso de messageStore.is_valid
        messageStore += (
            MessageData(**{
                'Name': sender,
                'ID': sender_id,
                'Date': date,
                'Time': time,
                'Message': message,
                'FileAttached': file_attached,
                'IsApple': True
            })
        )

    return messageStore.messages

def extract_info_android(whatsapp_contact, input_file: FileLike, attachment_files: Tuple[str]) -> TMessageData:
    messageStore = MessagesStore()
    uniqueIds = UniqueIdsStore()

    for line in read_file_lines(input_file):
        print(line)
        sender: Optional[str] = None
        sender_id: Optional[int] = None
        date: Optional[str] = None
        time: Optional[str] = None
        message: Optional[str] = None
        file_attached: StrOrFalse = False

        date, time = extract_datetime(datetime_pattern_android, line)
        sender, message = extract_sender_message(message_pattern_android, line)

        if not (sender or message):
            continue
        # TODO DEBUGER AQUI E VER COMO ESTA ESSE OBJETO
        uniqueIds += sender
        sender_id = uniqueIds.unique_ids[sender]

        if sender == whatsapp_contact:
            sender_id = 2
        else:
            sender_id = uniqueIds.unique_ids[sender]


        if uniqueIds.is_groupchat:
            return uniqueIds.unsupported_groupchat_err

        attachment_test = re.split(attachment_pattern_android, message) or ()
        if attachment_test:
            file_attached = next(
                (test[:255] for test in attachment_test if test[:255] in attachment_files),
                None
            )
            if file_attached:
                message = attached_message(file_attached)

        # print(f"attachment_test={attachment_test} attachment_files={attachment_files} has_attachment={has_attachment} attached_filename={attached_filename}")
        filetype = parse_filetype(file_attached)

        match filetype:
            # case w if w in (FileParsingMethod.MEDIA, FileParsingMethod.PDF):
            case FileParsingMethod.OFFICE:
                file_attached, _ = remove_ext(file_attached)
                file_attached += '.pdf'


        # Apenas vai adicionar no caso de messageStore.is_valid
        messageStore += (
            MessageData(**{
                'Name': sender,
                'ID': sender_id,
                'Date': date,
                'Time': time,
                'Message': message,
                'FileAttached': file_attached,
                'IsApple': False,
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
