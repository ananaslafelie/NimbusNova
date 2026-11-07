"""
TEST_UPLOAD.py - Test simplu pentru upload
"""
import asyncio
from nicegui import ui, events

def main():
    ui.label('Test Upload').classes('text-2xl')
    
    async def handle_upload(e: events.UploadEventArguments):
        print(f"\n=== UPLOAD EVENT ===")
        print(f"Type: {type(e)}")
        print(f"Dir: {[a for a in dir(e) if not a.startswith('_')]}")
        
        # Try to access e.file
        if hasattr(e, 'file'):
            f = e.file
            print(f"\nFile object type: {type(f)}")
            print(f"File dir: {[a for a in dir(f) if not a.startswith('_')]}")
            
            # Try different ways to get content
            for attr in ['name', 'filename', 'content', 'data', 'body', 'text', 'file', 'size']:
                if hasattr(f, attr):
                    val = getattr(f, attr)
                    print(f"  f.{attr}: {type(val)} = {repr(val)[:50] if val else 'None/empty'}")
            
            # Try read methods
            for method in ['read', 'read_text', 'read_bytes', 'text', 'json']:
                if hasattr(f, method):
                    try:
                        if callable(getattr(f, method)):
                            result = getattr(f, method)()
                            if asyncio.iscoroutine(result):
                                result = await result
                            print(f"  f.{method}(): {type(result)} = {repr(result)[:50] if result else 'None/empty'}")
                        else:
                            print(f"  f.{method} is not callable")
                    except Exception as ex:
                        print(f"  f.{method}() error: {ex}")
        else:
            print("No 'file' attribute on event")
            # Try direct attributes
            for attr in ['name', 'content', 'data', 'body', 'text']:
                if hasattr(e, attr):
                    val = getattr(e, attr)
                    print(f"  e.{attr}: {type(val)} = {repr(val)[:50] if val else 'None/empty'}")
        
        ui.label('Upload primit!').classes('text-green-500')
    
    ui.upload(on_upload=handle_upload, auto_upload=True).classes('w-full')
    
    ui.run(port=8082, reload=False)

if __name__ == '__main__':
    main()
