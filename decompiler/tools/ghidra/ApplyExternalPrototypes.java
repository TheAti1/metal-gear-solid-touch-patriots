/* Prototypes for the imported C functions (154 of 183 had none, so every
 * return value from OpenAL / AudioToolbox / CoreGraphics / CoreFoundation /
 * OpenGL ES / libm reached the decompiled code as undefined4).
 *
 *   1. Ghidra's typeinfo archive mac_10.9/mac_osx.gdt, matched by name with the
 *      Mach-O leading underscore removed. Built-in C types (long, pointers)
 *      re-size to the program's 32-bit ARM data organization on resolve.
 *   2. The iOS-only rest from the iOS 3.1 SDK headers (OpenGL ES 1.1 incl. the
 *      OES framebuffer extension, UIKit C functions, OpenAL, runtime helpers),
 *      parsed as C.
 *   Soft-float helpers (___addsf3vfp ...) are skipped: InstallSoftFloatCallFixup
 *   replaces every call with p-code, their prototype is never used.
 *
 * Applied to the EXTERNAL function and its __symbol_stub4 thunk.
 * Usage: analyzeHeadless ... -postScript ApplyExternalPrototypes.java  (idempotent)
 */
import java.io.File;
import java.util.*;

import ghidra.app.cmd.function.ApplyFunctionSignatureCmd;
import ghidra.app.script.GhidraScript;
import ghidra.app.util.cparser.C.CParserUtils;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;

public class ApplyExternalPrototypes extends GhidraScript {

    static final String[] MANUAL = {
        // OpenGL ES 1.1 (GLenum/GLbitfield = unsigned int, GLint/GLsizei = int, GLfloat = float, GLclampf = float)
        "void glBindFramebufferOES(unsigned int target, unsigned int framebuffer)",
        "void glBindRenderbufferOES(unsigned int target, unsigned int renderbuffer)",
        "void glBindTexture(unsigned int target, unsigned int texture)",
        "void glBlendFunc(unsigned int sfactor, unsigned int dfactor)",
        "unsigned int glCheckFramebufferStatusOES(unsigned int target)",
        "void glClear(unsigned int mask)",
        "void glClipPlanef(unsigned int plane, float * equation)",
        "void glColor4f(float red, float green, float blue, float alpha)",
        "void glDeleteFramebuffersOES(int n, unsigned int * framebuffers)",
        "void glDeleteRenderbuffersOES(int n, unsigned int * renderbuffers)",
        "void glDeleteTextures(int n, unsigned int * textures)",
        "void glDisable(unsigned int cap)",
        "void glDrawArrays(unsigned int mode, int first, int count)",
        "void glEnable(unsigned int cap)",
        "void glEnableClientState(unsigned int array)",
        "void glFramebufferRenderbufferOES(unsigned int target, unsigned int attachment, unsigned int renderbuffertarget, unsigned int renderbuffer)",
        "void glGenFramebuffersOES(int n, unsigned int * framebuffers)",
        "void glGenRenderbuffersOES(int n, unsigned int * renderbuffers)",
        "void glGenTextures(int n, unsigned int * textures)",
        "unsigned int glGetError(void)",
        "void glGetIntegerv(unsigned int pname, int * params)",
        "void glGetRenderbufferParameterivOES(unsigned int target, unsigned int pname, int * params)",
        "void glLoadIdentity(void)",
        "void glMatrixMode(unsigned int mode)",
        "void glOrthof(float left, float right, float bottom, float top, float zNear, float zFar)",
        "void glScissor(int x, int y, int width, int height)",
        "void glTexCoordPointer(int size, unsigned int type, int stride, void * pointer)",
        "void glTexEnvf(unsigned int target, unsigned int pname, float param)",
        "void glTexEnvi(unsigned int target, unsigned int pname, int param)",
        "void glTexImage2D(unsigned int target, int level, int internalformat, int width, int height, int border, unsigned int format, unsigned int type, void * pixels)",
        "void glTexParameteri(unsigned int target, unsigned int pname, int param)",
        "void glVertexPointer(int size, unsigned int type, int stride, void * pointer)",
        "void glViewport(int x, int y, int width, int height)",
        // OpenAL 1.1 (ALenum = int, ALuint = unsigned int, ALfloat = float, ALsizei = int)
        "void alDeleteBuffers(int n, unsigned int * buffers)",
        "void alDeleteSources(int n, unsigned int * sources)",
        "void alDistanceModel(int distanceModel)",
        "void alDopplerFactor(float value)",
        "void alGenBuffers(int n, unsigned int * buffers)",
        "void alGenSources(int n, unsigned int * sources)",
        "int alGetError(void)",
        "void alGetSourcei(unsigned int source, int param, int * value)",
        "void alListener3f(int param, float v1, float v2, float v3)",
        "void alListenerfv(int param, float * values)",
        "void alSource3f(unsigned int source, int param, float v1, float v2, float v3)",
        "void alSourcePause(unsigned int source)",
        "void alSourcePlay(unsigned int source)",
        "void alSourceStop(unsigned int source)",
        "void alSourcef(unsigned int source, int param, float value)",
        "void alSourcei(unsigned int source, int param, int value)",
        "char alcCloseDevice(void * device)",
        "void * alcCreateContext(void * device, int * attrlist)",
        "void alcDestroyContext(void * context)",
        "void * alcGetProcAddress(void * device, char * funcname)",
        "char alcMakeContextCurrent(void * context)",
        "void * alcOpenDevice(char * devicename)",
        // UIKit / Foundation C functions
        "int UIApplicationMain(int argc, char * * argv, void * principalClassName, void * delegateClassName)",
        "void UIGraphicsPushContext(void * context)",
        "void UIGraphicsPopContext(void)",
        "void NSLog(void * format, ...)",
        "void * NSSearchPathForDirectoriesInDomains(unsigned int directory, unsigned int domainMask, char expandTilde)",
        // AudioToolbox (OSStatus = int, UInt32 = unsigned int, opaque refs = void *)
        "int AudioFileClose(void * inAudioFile)",
        "int AudioFileGetProperty(void * inAudioFile, unsigned int inPropertyID, unsigned int * ioDataSize, void * outPropertyData)",
        "int AudioFileGetPropertyInfo(void * inAudioFile, unsigned int inPropertyID, unsigned int * outDataSize, unsigned int * isWritable)",
        "int AudioFileOpenURL(void * inFileRef, char inPermissions, unsigned int inFileTypeHint, void * * outAudioFile)",
        "int AudioFileReadBytes(void * inAudioFile, char inUseCache, long long inStartingByte, unsigned int * ioNumBytes, void * outBuffer)",
        "int AudioFileReadPackets(void * inAudioFile, char inUseCache, unsigned int * outNumBytes, void * outPacketDescriptions, long long inStartingPacket, unsigned int * ioNumPackets, void * outBuffer)",
        "int AudioQueueAllocateBuffer(void * inAQ, unsigned int inBufferByteSize, void * * outBuffer)",
        "int AudioQueueDispose(void * inAQ, char inImmediate)",
        "int AudioQueueEnqueueBuffer(void * inAQ, void * inBuffer, unsigned int inNumPacketDescs, void * inPacketDescs)",
        "int AudioQueueFreeBuffer(void * inAQ, void * inBuffer)",
        "int AudioQueueGetProperty(void * inAQ, unsigned int inID, void * outData, unsigned int * ioDataSize)",
        "int AudioQueueNewOutput(void * inFormat, void * inCallbackProc, void * inUserData, void * inCallbackRunLoop, void * inCallbackRunLoopMode, unsigned int inFlags, void * * outAQ)",
        "int AudioQueuePause(void * inAQ)",
        "int AudioQueuePrime(void * inAQ, unsigned int inNumberOfFramesToPrepare, unsigned int * outNumberOfFramesPrepared)",
        "int AudioQueueRemovePropertyListener(void * inAQ, unsigned int inID, void * inProc, void * inUserData)",
        "int AudioQueueSetParameter(void * inAQ, unsigned int inParamID, float inValue)",
        "int AudioQueueSetProperty(void * inAQ, unsigned int inID, void * inData, unsigned int inDataSize)",
        "int AudioQueueStart(void * inAQ, void * inStartTime)",
        "int AudioQueueStop(void * inAQ, char inImmediate)",
        "void AudioServicesPlaySystemSound(unsigned int inSystemSoundID)",
        "int AudioSessionInitialize(void * inRunLoop, void * inRunLoopMode, void * inInterruptionListener, void * inClientData)",
        "int AudioSessionSetActive(char active)",
        "int AudioSessionSetProperty(unsigned int inID, unsigned int inDataSize, void * inData)",
        // CoreFoundation
        "double CFAbsoluteTimeGetCurrent(void)",
        "void CFRelease(void * cf)",
        "void * CFRunLoopGetCurrent(void)",
        "void * CFURLCreateFromFileSystemRepresentation(void * allocator, char * buffer, int bufLen, char isDirectory)",
        // CoreGraphics (CGFloat = float on armv6, size_t = unsigned int)
        "char CGAffineTransformIsIdentity(CGAffineTransform t)",
        "CGAffineTransform CGAffineTransformScale(CGAffineTransform t, float sx, float sy)",
        "void * CGBitmapContextCreate(void * data, unsigned int width, unsigned int height, unsigned int bitsPerComponent, unsigned int bytesPerRow, void * space, unsigned int bitmapInfo)",
        "void * CGColorSpaceCreateDeviceGray(void)",
        "void * CGColorSpaceCreateDeviceRGB(void)",
        "void CGColorSpaceRelease(void * space)",
        "void CGContextClearRect(void * c, CGRect rect)",
        "void CGContextConcatCTM(void * c, CGAffineTransform transform)",
        "void CGContextDrawImage(void * c, CGRect rect, void * image)",
        "void CGContextFillEllipseInRect(void * c, CGRect rect)",
        "void CGContextFillRect(void * c, CGRect rect)",
        "void CGContextRelease(void * c)",
        "void CGContextScaleCTM(void * c, float sx, float sy)",
        "void CGContextSetGrayFillColor(void * c, float gray, float alpha)",
        "void CGContextSetRGBFillColor(void * c, float red, float green, float blue, float alpha)",
        "void CGContextTranslateCTM(void * c, float tx, float ty)",
        "unsigned int CGImageGetAlphaInfo(void * image)",
        "void * CGImageGetColorSpace(void * image)",
        "unsigned int CGImageGetHeight(void * image)",
        "unsigned int CGImageGetWidth(void * image)",
        // runtime / libc / mach
        "void objc_enumerationMutation(void * obj)",
        "void * objc_begin_catch(void * exc)",
        "void objc_end_catch(void)",
        "void objc_setProperty(void * self, char * _cmd, int offset, void * newValue, char atomic, char shouldCopy)",
        "unsigned long long mach_absolute_time(void)",
        "long random(void)",
        "float sinf(float x)",
        "float cosf(float x)",
        "float sqrtf(float x)",
        "float atan2f(float y, float x)",
        "double atan2(double y, double x)",
        "void _Unwind_SjLj_Register(void * fc)",
        "void _Unwind_SjLj_Unregister(void * fc)",
        "void _Unwind_SjLj_Resume(void * exc)",
    };

    @Override
    protected void run() throws Exception {
        DataTypeManager dtm = currentProgram.getDataTypeManager();
        Map<String, FunctionDefinition> arch = new HashMap<>();
        File gdt = new File("D:/Patriots_MGS_Touch_PC/tools/ghidra_11.3.2_PUBLIC/Ghidra/Features/Base/data/typeinfo/mac_10.9/mac_osx.gdt");
        FileDataTypeManager fdtm = FileDataTypeManager.openFileArchive(gdt, false);
        try {
            for (Iterator<DataType> it = fdtm.getAllDataTypes(); it.hasNext(); ) {
                DataType t = it.next();
                if (t instanceof FunctionDefinition) arch.putIfAbsent(t.getName(), (FunctionDefinition) t);
            }
            // CGAffineTransform {a, b, c, d, tx, ty} (CGFloat = float)
            StructureDataType at = new StructureDataType(new CategoryPath("/mgst"), "CGAffineTransform", 0);
            for (String f : new String[]{"a", "b", "c", "d", "tx", "ty"}) at.add(FloatDataType.dataType, 4, f, null);
            dtm.resolve(at, DataTypeConflictHandler.KEEP_HANDLER);
            Map<String, FunctionDefinition> manual = new HashMap<>();
            // C++ runtime (names are not C identifiers)
            FunctionDefinitionDataType nw = new FunctionDefinitionDataType("operator_new");
            nw.setReturnType(new PointerDataType(VoidDataType.dataType));
            nw.setArguments(new ParameterDefinition[]{new ParameterDefinitionImpl("size", UnsignedIntegerDataType.dataType, null)});
            FunctionDefinitionDataType dl = new FunctionDefinitionDataType("operator_delete");
            dl.setReturnType(VoidDataType.dataType);
            dl.setArguments(new ParameterDefinition[]{new ParameterDefinitionImpl("p", new PointerDataType(VoidDataType.dataType), null)});
            manual.put("operator.new", nw); manual.put("operator.new[]", nw);
            manual.put("operator.delete", dl); manual.put("operator.delete[]", dl);
            for (String proto : MANUAL) {
                FunctionDefinitionDataType fd = CParserUtils.parseSignature((ghidra.app.services.DataTypeManagerService) null,
                        currentProgram, proto, true);
                if (fd == null) { printerr("parse failed: " + proto); continue; }
                manual.put(fd.getName(), fd);
            }
            int fromArch = 0, fromManual = 0, skippedFloat = 0, none = 0;
            List<String> missing = new ArrayList<>();
            for (Function ext : currentProgram.getFunctionManager().getExternalFunctions()) {
                String n = ext.getName();
                String bare = n.startsWith("_") ? n.substring(1) : n;
                if (n.startsWith("___") && n.endsWith("vfp") || n.equals("___divsi3") || n.equals("___modsi3")
                        || n.equals("___udivsi3")) { skippedFloat++; continue; }
                if (n.startsWith("_objc_msgSend")) continue;     // done by FixSplitsAndStubs
                FunctionDefinition fd = manual.containsKey(bare) ? manual.get(bare) : arch.get(bare);
                if (fd == null) { none++; missing.add(n); continue; }
                FunctionDefinition res = (FunctionDefinition) dtm.resolve(fd, DataTypeConflictHandler.DEFAULT_HANDLER);
                List<Function> targets = new ArrayList<>();
                targets.add(ext);
                for (ghidra.program.model.address.Address a : ext.getFunctionThunkAddresses(true) == null
                        ? new ghidra.program.model.address.Address[0] : ext.getFunctionThunkAddresses(true)) {
                    Function t = getFunctionAt(a);
                    if (t != null) targets.add(t);
                }
                for (Function f : targets) {
                    new ApplyFunctionSignatureCmd(f.getEntryPoint(), res, SourceType.IMPORTED).applyTo(currentProgram, monitor);
                }
                if (manual.containsKey(bare)) fromManual++; else fromArch++;
            }
            println("external prototypes: from mac_osx.gdt " + fromArch + ", from iOS SDK table " + fromManual
                    + ", soft-float/int helpers skipped " + skippedFloat + ", still untyped " + none + " " + missing);
        } finally {
            fdtm.close();
        }
    }
}
