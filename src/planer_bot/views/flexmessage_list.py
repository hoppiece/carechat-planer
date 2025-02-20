from linebot.v3.messaging import (  # type: ignore
    FlexBox,
    FlexBubble,
    FlexText,
    PostbackAction,
)


def generate_list_flex_bubble(  # type: ignore [no-any-unimported]
    labels: list[str], title: str | None = None, text_align: str = "center"
) -> FlexBubble:
    """
    Flex Message のボタンリストを生成

    Args:
        labels (list[str]): ボタンに表示するラベルのリスト
        title (str | None, optional): タイトル（省略可）
        text_align (str, optional): ボタン内の文字揃え ("center" または "left"). Defaults to "center".

    Returns:
        FlexBubble: 生成された Flex Message のバブル
    """

    container = FlexBubble()
    container.body = FlexBox(layout="vertical", contents=[])

    if title:
        title_text = FlexText(text=title, weight="bold", size="lg")
        container.body.contents.append(title_text)

    name_list_box_contents = []
    for label in labels:
        # align オプションの適用
        padding_left = "md" if text_align == "left" else "none"

        # ボタン風のデザインを FlexBox で作成（ここにアクションを設定）
        name_box = FlexBox(
            layout="vertical",
            backgroundColor="#06c755", # LINE の緑
            cornerRadius="md",  # 角丸
            paddingAll="lg",  # 内側の余白を増やしてボタンを大きく
            #height="60px",  # ボタンの高さを強制的に大きくする
            justifyContent="center",  # テキストを縦中央配置
            alignItems=text_align,  # ボタン内でのテキスト配置
            paddingLeft=padding_left,  # 左揃えの場合は余白を追加
            action=PostbackAction(  # ここにアクションを設定（ボタン全体をタップ可能に）
                label=label,
                data=label,
                displayText=label,
            ),
            contents=[
                FlexText(
                    text=label,
                    weight="bold",
                    color="#FFFFFF",  # テキストを白に
                    #align=text_alignment,  # 中央揃え or 左揃え
                    #size="lg",  # 文字サイズを大きくしてボタン全体を大きく
                    wrap=True,  # テキストの折り返しを有効にする
                )
            ]
        )
        name_list_box_contents.append(name_box)

    name_list_box = FlexBox(
        layout="vertical", margin="md", spacing="sm", contents=name_list_box_contents
    )
    container.body.contents.append(name_list_box)

    return container

