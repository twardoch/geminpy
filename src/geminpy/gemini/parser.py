# this_file: src/geminpy/gemini/parser.py
"""Parses and cleans Gemini CLI output."""

from loguru import logger


class ResponseParser:
    """Parses and cleans Gemini CLI output."""

    AUTH_PATTERNS = [
        "Code Assist login required",
        "Attempting to open authentication page",
        "Otherwise navigate to:",
        "https://accounts.google.com/o/oauth2",
        "Waiting for authentication...",
        "Authentication successful",
        "[dotenv@",
    ]

    def extract_clean_response(self, stdout: str) -> str | None:
        """Extract clean model response from mixed output."""
        lines = stdout.strip().split("\n")

        # Skip authentication-related lines and find the actual response
        response_lines = []
        found_auth_complete = False

        for line in lines:
            line = line.strip()

            # Skip dotenv messages
            if line.startswith("[dotenv@"):
                continue

            # Skip authentication messages
            if any(auth_phrase in line for auth_phrase in self.AUTH_PATTERNS):
                continue

            # Skip empty lines at the start
            if not line and not response_lines:
                continue

            # If we find "Waiting for authentication...", the next non-empty line is likely the response
            if "Waiting for authentication..." in stdout:
                found_auth_complete = True

            # Collect non-authentication content
            if line:
                response_lines.append(line)

        # Return the cleaned response
        if response_lines:
            # If there's authentication flow, the response is typically the last meaningful content
            if found_auth_complete and response_lines:
                # Find the first line after authentication that looks like a response
                for i, line in enumerate(response_lines):
                    if not any(
                        skip_phrase in line
                        for skip_phrase in [
                            "dotenv",
                            "Code Assist",
                            "Attempting",
                            "navigate",
                            "oauth2",
                            "Waiting",
                        ]
                    ):
                        # Return from this line to the end
                        return "\n".join(response_lines[i:])

            # Fallback: return all non-auth lines
            return "\n".join(response_lines)

        return None
