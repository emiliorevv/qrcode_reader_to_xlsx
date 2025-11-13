# main.py
import cv2
from qr_reader import read_qr_from_frame
from parser_qr import extract_employee_fields
from excel_utils import append_employee_row

def main():
    # En macOS suele funcionar mejor AVFOUNDATION:p
    cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        print("No se pudo abrir la cámara con AVFOUNDATION, intentando CAP_ANY...")
        cap = cv2.VideoCapture(0, cv2.CAP_ANY)
    if not cap.isOpened():
        print("No se pudo abrir la cámara 😭")
        return

    print("Presiona 'q' para salir.")
    last_raw = None  # anti-duplicado inmediato

    while True:
        ok, frame = cap.read()
        if not ok:
            print("No se pudo leer frame de la cámara.")
            break

        qr_texts = read_qr_from_frame(frame)
        if qr_texts:
            raw = qr_texts[0].strip()
            if raw and raw != last_raw:
                print(f"\nQR leído (crudo): {raw}")

                campos, err = extract_employee_fields(raw)
                if err:
                    print(f"⚠️  {err}. No se guardó. (Asegura que el QR tenga Nombre, Número y Área)")
                else:
                    append_employee_row(campos)
                    print(f"✅ Guardado: {campos}")
                    last_raw = raw  # evitar spam del mismo QR

                # feedback visual
                cv2.putText(frame, "QR OK", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Lector QR - Empleados", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
