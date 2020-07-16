# PlusMinus_Bot

Twitch Chat-Bot that monitors chat for a special voting method.

## Montoring

Checks every chat message for the following beginnings:

\+\- \/ \-\+ \/ haugeNeut \-\> Neutral

\+ \/ haugePlus -> Plus

\- \/ haugeMinu -> Minus

Posts an interim result every 20 seconds and an end result after 5 seconds of no additional votes.

Checks if more than 10 votes have been added before posting any result.


