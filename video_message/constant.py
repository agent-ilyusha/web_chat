# -- coding: utf-8
import cv2

FACES = cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
EYES = cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_eye.xml")
SMILES = cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_smile.xml")

pcs = set()
